"""Builders for assembling aind-data-schema Procedures from Smartsheet data."""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from aind_data_schema.components.reagent import (
    ProbeReagent,
    ProteinProbe,
    Reagent,
)
from aind_data_schema.components.injection_procedures import (
    InjectionDynamics,
    InjectionProfile,
    ViralMaterial,
)
from aind_data_schema.components.specimen_procedures import SpecimenProcedure
from aind_data_schema.components.subject_procedures import Surgery
from aind_data_schema.components.surgery_procedures import Injection
from aind_data_schema.core.procedures import Procedures
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.specimen_procedure_types import SpecimenProcedureType
from aind_data_schema_models.units import VolumeUnit

from exaspim_procedures_generation.exceptions import (
    DataValidationError,
    ErrorContext,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Date parsing helper
# ---------------------------------------------------------------------------


def _parse_date(raw: Any, context_sheet: str = "unknown") -> date | None:
    """Parse a raw Smartsheet value to a date.

    Parameters
    ----------
    raw : Any
        The cell value.
    context_sheet : str
        Sheet name for error reporting.

    Returns
    -------
    date | None
        Parsed date, or None if empty.
    """
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw
    text = str(raw).strip()
    if not text:
        return None
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%m/%d/%y %I:%M %p", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise DataValidationError(
        f"Could not parse date: '{text}'",
        context=ErrorContext(sheet=context_sheet, actual=raw),
    )


def _require_date(raw: Any, field: str, sheet: str) -> date:
    """Parse a date, raising if None or unparseable.

    Parameters
    ----------
    raw : Any
        The raw cell value.
    field : str
        Column name (for error reporting).
    sheet : str
        Sheet name (for error reporting).

    Returns
    -------
    date
        The parsed date.

    Raises
    ------
    DataValidationError
        If the date is missing or unparseable.
    """
    result = _parse_date(raw, context_sheet=sheet)
    if result is None:
        raise DataValidationError(
            f"Required date field '{field}' is empty.",
            context=ErrorContext(sheet=sheet, column=field),
        )
    return result


# ---------------------------------------------------------------------------
# Subject Procedures Builders (Injection)
# ---------------------------------------------------------------------------


def build_injection_surgery(
    mouse_tracker_row: dict[str, Any],
) -> Surgery | None:
    """Build a Surgery model containing Injection(s) from Mouse Tracker data.

    Supports up to 4 independent viral injections (Virus1-Virus4).

    Parameters
    ----------
    mouse_tracker_row : dict[str, Any]
        Row from the Mouse Tracker sheet.

    Returns
    -------
    Surgery | None
        Surgery model instance suitable for Procedures.subject_procedures,
        or None if no injections found.
    """
    injection_objects: list[Injection] = []

    for virus_num in range(1, 5):
        prefix = f"Virus{virus_num}"
        virus_name = str(mouse_tracker_row.get(prefix, "") or "").strip()
        if not virus_name:
            continue

        injection_date = _parse_date(
            mouse_tracker_row.get(f"{prefix} Injection Date"),
            context_sheet="Mouse Tracker",
        )

        virus_id = str(
            mouse_tracker_row.get(f"{prefix} ID", "") or ""
        ).strip()
        titer_raw = mouse_tracker_row.get(f"{prefix} Stock Titer (GC/mL)")

        # Volume — check stereotaxic first, then fall back to RO volume
        if virus_num == 4:
            volume_raw = mouse_tracker_row.get(
                "Stereotaxic Volume Injected (nL)"
            )
        else:
            volume_raw = mouse_tracker_row.get(
                f"{prefix} Stereotaxic Volume Injected (nL)"
            )

        # Fall back to retro-orbital volume (stored in µL for the whole mix)
        ro_volume_raw = None
        if not volume_raw:
            ro_volume_raw = mouse_tracker_row.get(
                "Virus Mix Total Volume injected RO (uL)"
            )

        # Build injection material
        vm_kwargs: dict[str, Any] = {"name": virus_name}
        if virus_id:
            vm_kwargs["tars_identifiers"] = {
                "virus_tars_id": virus_id,
                "prep_lot_number": virus_id,
            }
        if titer_raw:
            try:
                vm_kwargs["titer"] = int(float(str(titer_raw)))
            except (ValueError, TypeError):
                pass

        viral_material = ViralMaterial(**vm_kwargs)

        # Build injection dynamics
        dynamics_list: list[InjectionDynamics] = []
        if volume_raw:
            try:
                vol = float(str(volume_raw))
                if vol > 0:
                    dynamics_list.append(
                        InjectionDynamics(
                            profile=InjectionProfile.BOLUS,
                            volume=vol,
                            volume_unit=VolumeUnit.NL,
                        )
                    )
            except (ValueError, TypeError):
                pass
        elif ro_volume_raw:
            # RO volume is in µL — convert to nL for consistency
            try:
                vol_ul = float(str(ro_volume_raw))
                if vol_ul > 0:
                    vol_nl = vol_ul * 1000.0
                    dynamics_list.append(
                        InjectionDynamics(
                            profile=InjectionProfile.BOLUS,
                            volume=vol_nl,
                            volume_unit=VolumeUnit.NL,
                        )
                    )
            except (ValueError, TypeError):
                pass

        # dynamics is required by the schema — skip injection if no volume data
        if not dynamics_list:
            logger.warning(
                "No volume data found for %s — skipping injection.", prefix,
            )
            continue

        # Build injection object
        inj_kwargs: dict[str, Any] = {
            "injection_materials": [viral_material],
            "dynamics": dynamics_list,
        }

        injection_objects.append(Injection(**inj_kwargs))

    if not injection_objects:
        return None

    # Use the earliest injection date as the surgery date
    # (injection_date from the loop is the last parsed one; collect all dates)
    dates: list[date] = []
    for virus_num in range(1, 5):
        prefix = f"Virus{virus_num}"
        virus_name = str(mouse_tracker_row.get(prefix, "") or "").strip()
        if not virus_name:
            continue
        d = _parse_date(
            mouse_tracker_row.get(f"{prefix} Injection Date"),
            context_sheet="Mouse Tracker",
        )
        if d is not None:
            dates.append(d)

    surgery_date = min(dates) if dates else None

    return Surgery(
        start_date=surgery_date,
        procedures=injection_objects,
    )


# ---------------------------------------------------------------------------
# Specimen Procedures Builders
# ---------------------------------------------------------------------------


def build_delipidation(
    sample_tracking_row: dict[str, Any],
    specimen_id: str,
    qc_notes: str | None = None,
) -> SpecimenProcedure:
    """Build a Delipidation SpecimenProcedure.

    Two phases: DCM (dichloromethane) and SBiP (sodium dodecylsulfate,
    butanol, isopropanol).

    Parameters
    ----------
    sample_tracking_row : dict[str, Any]
        Row from Sample Tracking sheet.
    specimen_id : str
        The specimen identifier.
    qc_notes : str | None
        Optional QC notes to attach.

    Returns
    -------
    SpecimenProcedure
        The delipidation procedure.
    """
    start_date = _require_date(
        sample_tracking_row.get("DCM Delipidation Start"),
        "DCM Delipidation Start",
        "Sample Tracking",
    )
    end_date = _require_date(
        sample_tracking_row.get("SBiP Delipidation End"),
        "SBiP Delipidation End",
        "Sample Tracking",
    )

    reagents = [
        Reagent(
            name="Dichloromethane (DCM)",
            source=Organization.OTHER,
        ),
        Reagent(
            name="SBiP (Sodium dodecylsulfate, Butanol, isoPropanol)",
            source=Organization.OTHER,
        ),
    ]

    return SpecimenProcedure(
        procedure_type=SpecimenProcedureType.DELIPIDATION,
        procedure_name="Delipidation (DCM + SBiP)",
        specimen_id=specimen_id,
        start_date=start_date,
        end_date=end_date,
        experimenters=[],
        procedure_details=reagents,
        notes=qc_notes,
    )


def build_immunolabeling(
    sample_tracking_row: dict[str, Any],
    specimen_id: str,
    qc_notes: str | None = None,
) -> SpecimenProcedure:
    """Build an Immunolabeling SpecimenProcedure.

    Includes primary and secondary antibody staining steps.

    Parameters
    ----------
    sample_tracking_row : dict[str, Any]
        Row from Sample Tracking sheet.
    specimen_id : str
        The specimen identifier.
    qc_notes : str | None
        Optional QC notes to attach.

    Returns
    -------
    SpecimenProcedure
        The immunolabeling procedure.
    """
    start_date = _require_date(
        sample_tracking_row.get("Immuno: Primary Ab Start Date"),
        "Immuno: Primary Ab Start Date",
        "Sample Tracking",
    )
    # End date is the secondary start + some duration; use secondary start as end
    secondary_start = _parse_date(
        sample_tracking_row.get("Immuno: Secondary Ab Start Date"),
        context_sheet="Sample Tracking",
    )
    end_date = secondary_start or start_date

    reagents: list[ProbeReagent] = []

    # Build primary antibody reagents (up to 3)
    for i in range(1, 4):
        ab_name = str(
            sample_tracking_row.get(f"Immuno: Primary Antibody{i}", "") or ""
        ).strip()
        if not ab_name:
            continue
        catalog = str(
            sample_tracking_row.get(f"Primary Antibody{i} Catalog #", "") or ""
        ).strip()
        lot = str(
            sample_tracking_row.get(f"Primary Antibody{i} Lot #", "") or ""
        ).strip()
        mass_raw = sample_tracking_row.get(
            f"Mass of Primary Antibody{i} used per Brain (ug)", ""
        )
        try:
            mass = float(str(mass_raw)) if mass_raw else 0.0
        except (ValueError, TypeError):
            mass = 0.0

        reagent = ProbeReagent(
            name=f"Primary Antibody: {ab_name}",
            source=Organization.OTHER,
            lot_number=lot if lot else None,
            target=ProteinProbe(
                protein=PIDName(name=ab_name),
                mass=mass,
            ),
        )
        reagents.append(reagent)

    # Build secondary antibody reagents (up to 3)
    for i in range(1, 4):
        ab_name = str(
            sample_tracking_row.get(f"Immuno: Secondary Antibody{i}", "") or ""
        ).strip()
        if not ab_name:
            continue
        catalog = str(
            sample_tracking_row.get(f"Secondary Antibody{i} Catalog #", "") or ""
        ).strip()
        lot = str(
            sample_tracking_row.get(f"Secondary Antibody{i} Lot #", "") or ""
        ).strip()
        mass_raw = sample_tracking_row.get(
            f"Mass of Secondary Antibody{i} used per Brain (ug)", ""
        )
        try:
            mass = float(str(mass_raw)) if mass_raw else 0.0
        except (ValueError, TypeError):
            mass = 0.0

        reagent = ProbeReagent(
            name=f"Secondary Antibody: {ab_name}",
            source=Organization.OTHER,
            lot_number=lot if lot else None,
            target=ProteinProbe(
                protein=PIDName(name=ab_name),
                mass=mass,
            ),
        )
        reagents.append(reagent)

    # Build notes about RRID if available
    primary_rrid = str(
        sample_tracking_row.get("Primary Antibody RRID", "") or ""
    ).strip()
    secondary_rrid = str(
        sample_tracking_row.get("Secondary Antibody RRID", "") or ""
    ).strip()
    rrid_notes = []
    if primary_rrid:
        rrid_notes.append(f"Primary RRID: {primary_rrid}")
    if secondary_rrid:
        rrid_notes.append(f"Secondary RRID: {secondary_rrid}")

    notes_parts = []
    if rrid_notes:
        notes_parts.append("; ".join(rrid_notes))
    if qc_notes:
        notes_parts.append(qc_notes)

    return SpecimenProcedure(
        procedure_type=SpecimenProcedureType.IMMUNOLABELING,
        procedure_name="Primary + Secondary Immunolabelling",
        specimen_id=specimen_id,
        start_date=start_date,
        end_date=end_date,
        experimenters=[],
        procedure_details=reagents,
        notes="; ".join(notes_parts) if notes_parts else None,
    )


def build_gelation(
    sample_tracking_row: dict[str, Any],
    specimen_id: str,
    qc_notes: str | None = None,
) -> SpecimenProcedure:
    """Build a Gelation SpecimenProcedure.

    Covers sub-steps: MBS, AcX, PBS wash, StockX+VA-044 equilibration,
    ProK digestion, PBS wash, 4C storage.

    Parameters
    ----------
    sample_tracking_row : dict[str, Any]
        Row from Sample Tracking sheet.
    specimen_id : str
        The specimen identifier.
    qc_notes : str | None
        Optional QC notes (e.g., digestion QC).

    Returns
    -------
    SpecimenProcedure
        The gelation procedure.
    """
    start_date = _require_date(
        sample_tracking_row.get("Gelation: MBS Start"),
        "Gelation: MBS Start",
        "Sample Tracking",
    )
    # End date: storage date or PBS Wash End
    storage_date = _parse_date(
        sample_tracking_row.get("Date of Storage in PBS Az 0.05% @4C"),
        context_sheet="Sample Tracking",
    )
    pbs_wash_end = _parse_date(
        sample_tracking_row.get("PBS Wash End"),
        context_sheet="Sample Tracking",
    )
    end_date = storage_date or pbs_wash_end or start_date

    reagents = [
        Reagent(name="MBS (m-Maleimidobenzoyl-N-hydroxysuccinimide ester)", source=Organization.OTHER),
        Reagent(name="Acryloyl-X (AcX)", source=Organization.OTHER),
        Reagent(name="Stock X + VA-044", source=Organization.OTHER),
        Reagent(name="Proteinase K (ProK)", source=Organization.OTHER),
        Reagent(name="PBS", source=Organization.OTHER),
    ]

    # Build protocol parameters with sub-step timing
    protocol_params: dict[str, str] = {}
    substep_dates = [
        ("MBS Start", "Gelation: MBS Start"),
        ("MBS End", "Gelation: MBS End"),
        ("AcX Start", "Gelation: AcX Start"),
        ("AcX End", "Gelation: AcX End"),
        ("PBS Wash Start", "Gelation: PBS Wash Start"),
        ("PBS Wash End", "Gelation: PBS Wash End"),
        ("StockX Equilibration Start", "Gelation: Stock X + VA-044 Equilibration  Start"),
        ("StockX Equilibration End", "Gelation: Stock X + VA-044 Equilibration End"),
        ("ProK RT Start", "Gelation +  ProK RT Start"),
        ("ProK RT End", "Gelation +  ProK RT End"),
        ("ProK 37C Start", "Gelation + Add'l ProK 37C Start"),
        ("ProK 37C End", "Gelation + Add'l ProK 37C End"),
        ("PBS Wash Start (post-gel)", "PBS Wash Start"),
        ("PBS Wash End (post-gel)", "PBS Wash End"),
        ("4C Storage Date", "Date of Storage in PBS Az 0.05% @4C"),
    ]
    for param_key, col_name in substep_dates:
        val = sample_tracking_row.get(col_name)
        if val is not None:
            protocol_params[param_key] = str(val)

    return SpecimenProcedure(
        procedure_type=SpecimenProcedureType.GELATION,
        procedure_name="Gelation (MBS, AcX, StockX+VA-044, ProK digestion)",
        specimen_id=specimen_id,
        start_date=start_date,
        end_date=end_date,
        experimenters=[],
        procedure_details=reagents,
        protocol_parameters=protocol_params if protocol_params else None,
        notes=qc_notes,
    )


def build_expansion(
    sample_tracking_row: dict[str, Any],
    specimen_id: str,
    qc_notes: str | None = None,
) -> SpecimenProcedure | None:
    """Build an Expansion SpecimenProcedure.

    Parameters
    ----------
    sample_tracking_row : dict[str, Any]
        Row from Sample Tracking sheet.
    specimen_id : str
        The specimen identifier.
    qc_notes : str | None
        Optional QC notes.

    Returns
    -------
    SpecimenProcedure | None
        The expansion procedure, or None if expansion dates are not available.
    """
    start_date = _parse_date(
        sample_tracking_row.get("Expansion Start Date"),
        context_sheet="Sample Tracking",
    )
    end_date = _parse_date(
        sample_tracking_row.get("Expansion End Date"),
        context_sheet="Sample Tracking",
    )
    if start_date is None or end_date is None:
        logger.info("Expansion dates not available — skipping expansion step.")
        return None

    # Reagent sources TBD — placeholder for now
    reagents = [
        Reagent(name="Expansion solution", source=Organization.OTHER),
    ]

    return SpecimenProcedure(
        procedure_type=SpecimenProcedureType.EXPANSION,
        procedure_name="Expansion",
        specimen_id=specimen_id,
        start_date=start_date,
        end_date=end_date,
        experimenters=[],
        procedure_details=reagents,
        notes=qc_notes,
    )


def build_screening_imaging(
    sample_tracking_row: dict[str, Any],
    specimen_id: str,
    screening_type: str,
    qc_notes: str | None = None,
) -> SpecimenProcedure | None:
    """Build a screening imaging SpecimenProcedure (type=OTHER).

    These are intermediate QC imaging steps (smartSPIM or 1x exaSPIM).

    Parameters
    ----------
    sample_tracking_row : dict[str, Any]
        Row from Sample Tracking sheet.
    specimen_id : str
        The specimen identifier.
    screening_type : str
        Either "smartSPIM" or "1x exaSPIM".
    qc_notes : str | None
        Optional QC/screening notes.

    Returns
    -------
    SpecimenProcedure | None
        The screening procedure, or None if no date available.
    """
    # Screening imaging dates may come from QC sheet or notes columns
    # For now, we create this as a placeholder from QC data
    if not qc_notes:
        return None

    # We don't have explicit date columns for screening in Sample Tracking,
    # so we'll use a reasonable placeholder approach
    return SpecimenProcedure(
        procedure_type=SpecimenProcedureType.OTHER,
        procedure_name=f"{screening_type} Screening Imaging",
        specimen_id=specimen_id,
        start_date=date.today(),  # Will be overridden when date columns identified
        end_date=date.today(),
        experimenters=[],
        notes=f"{screening_type} screening: {qc_notes}",
    )


def build_mounting_and_imaging(
    imaging_queue_row: dict[str, Any],
    specimen_id: str,
    qc_notes: str | None = None,
) -> SpecimenProcedure:
    """Build a Mounting SpecimenProcedure for the final imaging step.

    Parameters
    ----------
    imaging_queue_row : dict[str, Any]
        Row from the Imaging Queue sheet.
    specimen_id : str
        The specimen identifier.
    qc_notes : str | None
        Optional QC notes.

    Returns
    -------
    SpecimenProcedure
        The mounting + imaging procedure.
    """
    start_date = _require_date(
        imaging_queue_row.get("Imaging Start Date"),
        "Imaging Start Date",
        "Imaging Queue",
    )
    end_date_raw = imaging_queue_row.get("Imaging End Date")
    end_date = _parse_date(end_date_raw, context_sheet="Imaging Queue") or start_date

    microscope = str(imaging_queue_row.get("Microscope", "") or "").strip()
    imaging_buffer = str(imaging_queue_row.get("Imaging Buffer", "") or "").strip()
    channels = str(imaging_queue_row.get("Signal channel(s)", "") or "").strip()
    notes_col = str(imaging_queue_row.get("Notes", "") or "").strip()

    reagents: list[Reagent] = []
    if imaging_buffer:
        reagents.append(
            Reagent(name=f"Imaging Buffer: {imaging_buffer}", source=Organization.OTHER)
        )

    notes_parts = []
    if microscope:
        notes_parts.append(f"Microscope: {microscope}")
    if channels:
        notes_parts.append(f"Signal channels: {channels}")
    if notes_col:
        notes_parts.append(f"Imaging notes: {notes_col}")
    if qc_notes:
        notes_parts.append(qc_notes)

    return SpecimenProcedure(
        procedure_type=SpecimenProcedureType.MOUNTING,
        procedure_name="Mounting and ExaSPIM Imaging",
        specimen_id=specimen_id,
        start_date=start_date,
        end_date=end_date,
        experimenters=[],
        procedure_details=reagents if reagents else [],
        notes="; ".join(notes_parts) if notes_parts else None,
    )


# ---------------------------------------------------------------------------
# QC Notes Helpers
# ---------------------------------------------------------------------------


def _extract_qc_notes(
    qc_rows: list[dict[str, Any]],
    category: str,
) -> str | None:
    """Extract QC notes for a specific category from QC sheet rows.

    Parameters
    ----------
    qc_rows : list[dict[str, Any]]
        Rows from the QC sheet.
    category : str
        The category key to look for.

    Returns
    -------
    str | None
        Combined notes, or None if empty.
    """
    column_mapping = {
        "perfusion": "Perfusion / Dissection Quality Notes",
        "immunolabeling": "Immuno Gross Anatomy Notes",
        "digestion": "Digestion Notes",
        "screening_1x": "1x screening notes - Platform lead",
        "screening_investigator": "1x screening notes - Investigator",
        "labeling_density": "Labeling Density Notes (Olympus MXV10)",
        "special": "Special Notes",
    }
    col = column_mapping.get(category)
    if not col:
        return None

    notes_parts = []
    for row in qc_rows:
        value = str(row.get(col, "") or "").strip()
        if value:
            notes_parts.append(value)

    return "; ".join(notes_parts) if notes_parts else None


# ---------------------------------------------------------------------------
# Top-Level Builder
# ---------------------------------------------------------------------------


def build_procedures(
    specimen_id: str,
    data: dict[str, list[dict[str, Any]]],
    perfusion_surgery: dict[str, Any] | None = None,
) -> Procedures:
    """Assemble the full Procedures object from all sheet data.

    Parameters
    ----------
    specimen_id : str
        The specimen/subject ID.
    data : dict[str, list[dict[str, Any]]]
        All fetched data keyed by reader name:
        "mouse_tracker", "sample_tracking", "imaging_queue", "qc_sheet".
    perfusion_surgery : dict[str, Any] | None
        Perfusion Surgery dict from metadata-service (if available).

    Returns
    -------
    Procedures
        The complete Procedures object ready for serialization.
    """
    mt_rows = data.get("mouse_tracker", [])
    st_rows = data.get("sample_tracking", [])
    iq_rows = data.get("imaging_queue", [])
    qc_rows = data.get("qc_sheet", [])

    # --- Subject Procedures ---
    subject_procedures: list[Any] = []

    # Add perfusion surgery from metadata-service if available
    if perfusion_surgery:
        subject_procedures.append(perfusion_surgery)

    # Build injection surgery from Mouse Tracker
    if mt_rows:
        injection_surgery = build_injection_surgery(mt_rows[0])
        if injection_surgery:
            subject_procedures.append(injection_surgery)

    # --- Specimen Procedures ---
    specimen_procedures: list[SpecimenProcedure] = []

    if st_rows:
        st_row = st_rows[0]

        # Step 5: Delipidation
        delip_notes = _extract_qc_notes(qc_rows, "special")
        specimen_procedures.append(
            build_delipidation(st_row, specimen_id, qc_notes=delip_notes)
        )

        # Step 6: Immunolabeling
        immuno_notes = _extract_qc_notes(qc_rows, "immunolabeling")
        specimen_procedures.append(
            build_immunolabeling(st_row, specimen_id, qc_notes=immuno_notes)
        )

        # Step 7: Gelation
        digestion_notes = _extract_qc_notes(qc_rows, "digestion")
        specimen_procedures.append(
            build_gelation(st_row, specimen_id, qc_notes=digestion_notes)
        )

        # Step 4: SmartSPIM Screening (if QC notes exist)
        screening_notes = _extract_qc_notes(qc_rows, "labeling_density")
        smartspim_proc = build_screening_imaging(
            st_row, specimen_id, "smartSPIM", qc_notes=screening_notes
        )
        if smartspim_proc:
            specimen_procedures.append(smartspim_proc)

        # Step 8: 1x exaSPIM Screening (if QC notes exist)
        exaspim_1x_notes = _extract_qc_notes(qc_rows, "screening_1x")
        exaspim_proc = build_screening_imaging(
            st_row, specimen_id, "1x exaSPIM", qc_notes=exaspim_1x_notes
        )
        if exaspim_proc:
            specimen_procedures.append(exaspim_proc)

        # Step 9: Expansion
        expansion_proc = build_expansion(st_row, specimen_id)
        if expansion_proc:
            specimen_procedures.append(expansion_proc)

    # Step 10: Mounting + Imaging
    if iq_rows:
        specimen_procedures.append(
            build_mounting_and_imaging(iq_rows[0], specimen_id)
        )

    # Sort specimen_procedures by start_date
    specimen_procedures.sort(key=lambda p: p.start_date)

    return Procedures(
        subject_id=specimen_id,
        subject_procedures=subject_procedures,
        specimen_procedures=specimen_procedures,
    )
