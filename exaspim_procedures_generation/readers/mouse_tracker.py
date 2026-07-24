"""Reader for the Mouse Tracker sheet (viral injections, perfusion info)."""

from __future__ import annotations

from exaspim_procedures_generation.readers.base import BaseSheetReader


class MouseTrackerReader(BaseSheetReader):
    """Reads viral injection and basic subject data from the Mouse Tracker sheet.

    The Mouse Tracker's "Mouse ID" column often contains cre-line annotations
    appended to the specimen ID, so this reader uses substring (contains)
    matching to locate the correct row.
    """

    sheet_label = "Mouse Tracker"
    id_column = "Mouse ID"
    required = True
    repeatable = False
    contains_match = True

    required_columns = [
        "Mouse ID",
        "Virus1 Injection Date",
        "Virus1",
        "Virus1 ID",
        "Virus1 Stock Titer (GC/mL)",
        "Virus1 Dose (GC)",
        "Virus1 AP (mm)",
        "Virus1 ML (mm)",
        "Virus1 DV (mm)",
        "Virus1 Stereotaxic Volume Injected (nL)",
        "Perfusion Date",
    ]
