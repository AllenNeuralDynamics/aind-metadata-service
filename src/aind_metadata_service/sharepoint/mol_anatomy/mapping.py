"""Module to handle parsing information into aind-data-schema models"""

import json
from typing import List

import pandas as pd
from aind_data_schema.procedures import RetroOrbitalInjection, SubjectProcedure
from office365.sharepoint.client_context import ClientContext

from aind_metadata_service.sharepoint.mol_anatomy.models import ExcelSheetRow


class MolecularAnatomyMapping:
    """Class that handles retrieving and parsing excel file into
    aind-data-schema models"""

    def get_procedures_from_sharepoint(
        self, subject_id: str, client_context: ClientContext, list_title: str
    ) -> List[SubjectProcedure]:
        """Gets procedures from excel file in Sharepoint"""
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
    def _apply_filter(
        excel_sheets: dict, subject_id: str
    ) -> List[ExcelSheetRow]:
        """Scan through the excel rows and take only the relevant rows with the
        subject_id."""
        list_of_records = []
        for sheet_name in [
            sn
            for sn in excel_sheets
            if not ExcelSheetRow.ignore_excel_sheet(
                excel_sheet_name=sn, column_names=excel_sheets[sn].columns
            )
        ]:
            sheet_df = excel_sheets[sheet_name]
            filter_df = sheet_df[sheet_df["Mouse ID"] == int(subject_id)]
            json_list = json.loads(filter_df.to_json(orient="records"))
            list_of_records.extend(
                [ExcelSheetRow.parse_obj(j) for j in json_list]
            )
        return list_of_records

    @staticmethod
    def map_model(sharepoint_model: ExcelSheetRow) -> List[SubjectProcedure]:
        """Maps a row in the excel sheet into a list of Procedures"""
        # Check if retro orbital injection present:
        if sharepoint_model.ro_injection_date is not None:
            ro_procedures = [
                RetroOrbitalInjection.construct(
                    start_date=sharepoint_model.ro_injection_date,
                    end_date=sharepoint_model.ro_injection_date,
                )
            ]
        else:
            ro_procedures = []
        return ro_procedures
