"""Reader for the Sample Processing QC sheet (quality notes)."""

from __future__ import annotations

from exaspim_procedures_generation.readers.base import BaseSheetReader


class QCSheetReader(BaseSheetReader):
    """Reads QC notes from the Sample Processing QC sheet.

    QC data is optional and may have multiple rows (e.g., multiple QC
    assessments). Notes will be attached to the relevant procedure steps.
    """

    sheet_label = "QC Sheet"
    id_column = "Mouse ID"
    required = False
    repeatable = True
    contains_match = False

    required_columns = [
        "Mouse ID",
    ]
