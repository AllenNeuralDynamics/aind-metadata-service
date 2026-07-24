"""CLI entry point and top-level orchestration for ExaSPIM procedures generation."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

from aind_data_schema.core.procedures import Procedures

from exaspim_procedures_generation.builders import build_procedures
from exaspim_procedures_generation.config import SheetName, load_settings
from exaspim_procedures_generation.metadata_service import (
    compare_perfusion_dates,
    fetch_subject_procedures,
    extract_perfusion_surgery,
)
from exaspim_procedures_generation.readers import (
    ImagingQueueReader,
    MouseTrackerReader,
    QCSheetReader,
    SampleTrackingReader,
)
from exaspim_procedures_generation.smartsheet_client import SmartsheetClient
from exaspim_procedures_generation.validators import (
    _parse_date,
    run_all_validations,
)

logger = logging.getLogger(__name__)


def _collect_rows(
    client: SmartsheetClient,
    settings_lookup: dict[SheetName, int],
    specimen_id: str,
) -> dict[str, list[dict[str, Any]]]:
    """Fetch all sheet rows needed for procedures generation.

    Parameters
    ----------
    client : SmartsheetClient
        The initialized Smartsheet client.
    settings_lookup : dict[SheetName, int]
        Mapping from SheetName to sheet ID.
    specimen_id : str
        The specimen identifier.

    Returns
    -------
    dict[str, list[dict[str, Any]]]
        All fetched data keyed by reader name.
    """
    rows: dict[str, list[dict[str, Any]]] = {}

    rows["mouse_tracker"] = MouseTrackerReader(
        client,
        settings_lookup[SheetName.MOUSE_TRACKER],
        specimen_id,
    ).fetch_rows()

    rows["sample_tracking"] = SampleTrackingReader(
        client,
        settings_lookup[SheetName.SAMPLE_TRACKING],
        specimen_id,
    ).fetch_rows()

    rows["imaging_queue"] = ImagingQueueReader(
        client,
        settings_lookup[SheetName.IMAGING_QUEUE],
        specimen_id,
    ).fetch_rows()

    rows["qc_sheet"] = QCSheetReader(
        client,
        settings_lookup[SheetName.QC_SHEET],
        specimen_id,
    ).fetch_rows()

    return rows


def generate_procedures(
    specimen_id: str,
    config_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    client: SmartsheetClient | None = None,
) -> Procedures:
    """Generate a Procedures JSON document for the given specimen.

    This is the primary API function. It orchestrates data fetching,
    validation, and building the Procedures object.

    Parameters
    ----------
    specimen_id : str
        The specimen identifier (used to find rows in each sheet).
    config_path : str | Path | None
        Path to JSON config file for sheet IDs. Uses defaults if None.
    output_dir : str | Path | None
        Directory to write procedures.json. If None, no file is written.
    client : SmartsheetClient | None
        Optional pre-configured client (for testing/DI).

    Returns
    -------
    Procedures
        The assembled Procedures object.
    """
    settings = load_settings(config_path)
    settings_lookup = {
        sheet: settings.get_sheet_id(sheet) for sheet in SheetName
    }
    smartsheet_client = client or SmartsheetClient(settings.smartsheet_access_token)

    # Fetch all rows from all sheets
    logger.info("Fetching data for specimen: %s", specimen_id)
    data = _collect_rows(smartsheet_client, settings_lookup, specimen_id)

    # Run all validations
    logger.info("Running validations...")
    run_all_validations(data)

    # Fetch perfusion surgery from metadata-service
    perfusion_surgery = None
    procedures_data = fetch_subject_procedures(specimen_id)
    if procedures_data:
        perfusion_surgery = extract_perfusion_surgery(procedures_data)

    # Cross-validate perfusion date if we have both sources
    mt_rows = data.get("mouse_tracker", [])
    if mt_rows and perfusion_surgery:
        raw_perf_date = mt_rows[0].get("Perfusion Date")
        ss_perf_date = _parse_date(raw_perf_date)
        if ss_perf_date:
            compare_perfusion_dates(specimen_id, ss_perf_date)

    # Build procedures
    logger.info("Building procedures...")
    procedures = build_procedures(specimen_id, data, perfusion_surgery)

    # Write output
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        procedures.write_standard_file(output_directory=str(output_path))
        logger.info("Wrote procedures.json to %s", output_path)

    return procedures


def cli() -> None:
    """Parse CLI arguments and run the procedures generation pipeline."""
    parser = argparse.ArgumentParser(
        prog="exaspim-procedures-generation",
        description=(
            "Generate AIND procedures.json for ExaSPIM specimens "
            "from Smartsheet metadata."
        ),
    )
    parser.add_argument(
        "--specimen-id",
        required=True,
        help="Specimen identifier used to locate rows in each Smartsheet.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to JSON config file mapping sheet names to IDs.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write procedures.json (default: current directory).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging.",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    try:
        procedures = generate_procedures(
            specimen_id=args.specimen_id,
            config_path=args.config,
            output_dir=args.output_dir,
        )
        # Validate the output can serialize properly
        _ = procedures.model_dump_json()
        logger.info("Successfully generated procedures for %s", args.specimen_id)
    except Exception as e:
        logger.error("Failed to generate procedures: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    cli()
