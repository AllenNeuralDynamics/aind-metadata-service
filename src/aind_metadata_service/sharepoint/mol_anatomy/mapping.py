from office365.sharepoint.client_context import ClientContext
import pandas as pd
from typing import List
from aind_metadata_service.sharepoint.mol_anatomy.models import ExcelSheetRow
import json
from aind_data_schema.procedures import (
    SubjectProcedure,
)


class MolecularAnatomyMapping:
    def get_procedures_from_sharepoint(
        self, subject_id: str, client_context: ClientContext, list_title: str
    ) -> List[SubjectProcedure]:
        file = (
            client_context.web.get_file_by_guest_url(list_title)
            .expand(["versions", "listItemAllFields"])
            .get()
            .execute_query()
        )
        file_bytes_stream = file.open_binary_stream()
        file_bytes = file_bytes_stream.execute_query()
        excel_sheets = pd.read_excel(file_bytes.value, sheet_name=None)
        records = self._apply_filter(
            excel_sheets=excel_sheets, subject_id=subject_id
        )
        procedures = []
        for record in records:
            procedures.extend(self.map_model(record))
        return procedures

    @staticmethod
    def _apply_filter(excel_sheets: dict, subject_id: str) -> List[ExcelSheetRow]:
        list_of_records = []
        for sheet_name in excel_sheets:
            sheet_df = excel_sheets[sheet_name]
            if 'Mouse ID' in sheet_df.columns:
                filter_df = sheet_df[sheet_df['Mouse ID'] == int(subject_id)]
                json_list = json.loads(filter_df.to_json(orient="records"))
                list_of_records.extend([ExcelSheetRow.parse_obj(j) for j in json_list])
        return list_of_records

    @staticmethod
    def map_model(sharepoint_model: ExcelSheetRow) -> List[SubjectProcedure]:
        return []



