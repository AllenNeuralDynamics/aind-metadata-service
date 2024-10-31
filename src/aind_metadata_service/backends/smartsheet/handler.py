"""Module to handle smartsheet api responses"""

from typing import Any, List, Type

from aind_smartsheet_api.client import SmartsheetClient
from pydantic import BaseModel

from aind_metadata_service.backends.smartsheet.models import (
    FundingModel,
    PerfusionsModel,
    ProtocolsModel,
)


class SessionHandler:
    """Handle session object to get data"""

    def __init__(self, session: SmartsheetClient):
        """Class constructor"""
        self.session = session

    def get_parsed_sheet(
        self, sheet_id: int, model: Type[BaseModel]
    ) -> List[Any]:
        """
        Converts the rows in a Smart Sheet into a Pydantic model
        Parameters
        ----------
        sheet_id : int
          ID number of smart sheet
        model : Type[BaseModel]
          Pydantic model to parse the sheet to

        Returns
        -------
        List[Any]
          A list of Pydantic models

        """
        sheet = self.session.get_parsed_sheet_model(
            sheet_id=sheet_id, model=model, validate=False
        )
        return sheet

    @staticmethod
    def get_project_funding_info(
        sheet_model: List[FundingModel], project_name: str
    ) -> List[FundingModel]:
        """
        Filters sheet by specific project name
        Parameters
        ----------
        sheet_model : List[FundingModel]
        project_name : str

        Returns
        -------
        List[FundingModel]
          In the event that there are multiple project names, will return
          A list of all of that match the project name.

        """

        filtered_rows = [
            r for r in sheet_model if r.project_name == project_name
        ]
        return filtered_rows

    @staticmethod
    def get_project_names(sheet_model: List[FundingModel]) -> List[str]:
        """
        Returns a sorted list of unique project names found in the Funding
        SmartSheet.
        Parameters
        ----------
        sheet_model : List[FundingModel]

        Returns
        -------
        List[str]

        """
        all_names = [
            r.project_name for r in sheet_model if r.project_name is not None
        ]
        sorted_names = sorted(list(set(all_names)))
        return sorted_names

    @staticmethod
    def get_protocols_info(
        sheet_model: List[ProtocolsModel], protocol_name: str
    ) -> List[ProtocolsModel]:
        """
        Filter protocols Smartsheet by protocols name
        Parameters
        ----------
        sheet_model : List[ProtocolsModel]
        protocol_name : str

        Returns
        -------
        List[ProtocolsModel]
          In the event that there are multiple project names, will return
          A list of all of that match the project name.

        """
        filtered_rows = [
            r for r in sheet_model if r.protocol_name == protocol_name
        ]
        return filtered_rows

    @staticmethod
    def get_perfusions_info(
        sheet_model: List[PerfusionsModel], subject_id: str
    ) -> List[PerfusionsModel]:
        """

        Parameters
        ----------
        sheet_model : List[PerfusionsModel]
        subject_id : str

        Returns
        -------
        List[PerfusionsModel]
          In the event that there are multiple project names, will return
          A list of all of that match the project name.
        """
        filtered_rows = [
            r for r in sheet_model if str(int(r.subject_id)) == subject_id
        ]
        return filtered_rows
