"""Reader for the Imaging Queue sheet (step 10: mounting + imaging)."""

from __future__ import annotations

from exaspim_procedures_generation.readers.base import BaseSheetReader


class ImagingQueueReader(BaseSheetReader):
    """Reads final imaging data from the Imaging Queue sheet.

    Covers the mounting and full-resolution imaging step (step 10).
    The ID column is "Sample" with exact matching.
    """

    sheet_label = "Imaging Queue"
    id_column = "Sample"
    required = True
    repeatable = False
    contains_match = False

    required_columns = [
        "Sample",
        "Imaging Start Date",
        "Imaging End Date",
        "Imaging Buffer",
        "Microscope",
        "Signal channel(s)",
    ]
