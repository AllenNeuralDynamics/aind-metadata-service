"""Reader for the ExM Sample Tracking sheet (steps 2-9)."""

from __future__ import annotations

from exaspim_procedures_generation.readers.base import BaseSheetReader


class SampleTrackingReader(BaseSheetReader):
    """Reads specimen processing data from the ExM Sample Tracking sheet.

    Covers delipidation, immunolabelling, gelation, screening, and expansion
    steps. The ID column is "Sample" with exact matching.
    """

    sheet_label = "Sample Tracking"
    id_column = "Sample"
    required = True
    repeatable = False
    contains_match = False

    required_columns = [
        "Sample",
        # Delipidation
        "DCM Delipidation Start",
        "DCM Delipidation End",
        "SBiP Delipidation Start",
        "SBiP Delipidation End",
        # Immunolabelling - Primary
        "Immuno: Primary Ab Start Date",
        "Immuno: Primary Antibody1",
        "Primary Antibody1 Catalog #",
        "Primary Antibody1 Lot #",
        # Immunolabelling - Secondary
        "Immuno: Secondary Ab Start Date",
        "Immuno: Secondary Antibody1",
        "Secondary Antibody1 Catalog #",
        "Secondary Antibody1 Lot #",
        # Gelation
        "Gelation: MBS Start",
        "Gelation: MBS End",
        "Gelation: AcX Start",
        "Gelation: AcX End",
        "Gelation: PBS Wash Start",
        "Gelation: PBS Wash End",
        "Gelation: Stock X + VA-044 Equilibration  Start",
        "Gelation: Stock X + VA-044 Equilibration End",
        "Gelation +  ProK RT Start",
        "Gelation +  ProK RT End",
        "Gelation + Add'l ProK 37C Start",
        "Gelation + Add'l ProK 37C End",
        "PBS Wash Start",
        "PBS Wash End",
        "Date of Storage in PBS Az 0.05% @4C",
        # Expansion
        "Expansion Start Date",
        "Expansion End Date",
    ]


# Columns for viral injection data in Sample Tracking (for cross-validation)
SAMPLE_TRACKING_INJECTION_COLUMNS = [
    "Virus1 Injection Date",
    "Virus1 Injection Type",
    "Virus1",
    "Virus1 ID",
    "Virus1 Stock Titer (GC/mL)",
    "Virus1 Dose (GC)",
    "Virus1 AP (mm)",
    "Virus1 ML (mm)",
    "Virus1 DV (mm)",
    "Virus1 Stereotaxic Volume Injected (nL)",
]
