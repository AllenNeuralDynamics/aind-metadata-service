"""Module that handles the methods to map the SmartSheet response to the
aind-data-schema Funding model."""

import logging
from typing import Any, Dict, List, Optional, Union

from aind_data_schema.core.data_description import Funding
from aind_data_schema.models.institutions import Institution
from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.client import SmartSheetClient
from aind_metadata_service.smartsheet.funding.models import (
    FundingColumnNames,
    FundingRow,
    FundingSheet,
)


class FundingMapper:
    """Primary class to handle mapping data models and returning a response"""

    def __init__(self, smart_sheet_client: SmartSheetClient):
        """
        Class Constructor
        Parameters
        ----------
        smart_sheet_client: SmartSheetClient
        """
        self.smart_sheet_client = smart_sheet_client

    @property
    def sheet_contents(self):
        """Return sheet contents as a json string."""
        return self.smart_sheet_client.get_sheet()

    @property
    def _column_id_map(self) -> Dict[str, Any]:
        """SmartSheet uses integer ids for the columns. We need a way to
        map the column titles to the ids so we can retrieve information using
        just the titles."""
        return {c.title: c.id for c in self.model.columns}

    @property
    def model(self) -> FundingSheet:
        """Convert sheet contents to a pydantic model"""
        return FundingSheet.model_validate_json(self.sheet_contents)

    @staticmethod
    def _parse_institution(input_name: str) -> Union[Institution, str]:
        """
        Generate Institution from string
        Parameters
        ----------
        input_name : str
          Institution name

        Returns
        -------
        Union[Institution, str]
          Either an Institution parsed from the name. If the Institution can't
          be generated from the name, then it returns the input name.

        """
        try:
            return Institution.from_name(input_name)
        except KeyError:
            return input_name

    def _map_row_to_funding(
        self, row: FundingRow, input_project_code: str
    ) -> Optional[Funding]:
        """
        Map a row to an optional funding model.
        Parameters
        ----------
        row : FundingRow
        input_project_code : str
          The project code the user inputs

        Returns
        -------
        Union[Funding, None]
          None if the project code in the row doesn't match the
          input_project_code. Otherwise, will try to return a valid Funding
          model. If there is some data entry mistake, then it will return a
          Funding model as good as it can.

        """
        project_code = None
        grant_number = None
        institution = None
        investigators = None
        for cell in row.cells:
            if (
                cell.columnId
                == self._column_id_map[FundingColumnNames.PROJECT_CODE.value]
            ):
                project_code = cell.value
            if (
                cell.columnId
                == self._column_id_map[FundingColumnNames.INSTITUTION.value]
            ):
                institution = cell.value
            if (
                cell.columnId
                == self._column_id_map[FundingColumnNames.GRANT_NUMBER.value]
            ):
                grant_number = cell.value
            if (
                cell.columnId
                == self._column_id_map[FundingColumnNames.INVESTIGATORS.value]
            ):
                investigators = cell.value
        if input_project_code != project_code:
            return None
        else:
            try:
                return Funding(
                    funder=self._parse_institution(institution),
                    grant_number=grant_number,
                    fundee=investigators,
                )
            except ValidationError:
                return Funding.model_construct(
                    funder=self._parse_institution(institution),
                    grant_number=grant_number,
                    fundee=investigators,
                )

    def _reduce_funding_list(
        self, funding_list: List[Funding]
    ) -> List[Funding]:
        """
        There are multiple rows associated with a single project code in the
        SmartSheet. This method reduces that information down so that there
        is one Funding model per (project_code, grant_number) by concatenating
        the investigators into a single string. In theory, there should only
        be one element in the return list, but we'll return everything in case
        there was a data-entry mistake.
        Parameters
        ----------
        funding_list : List[Funding]
          Each row for a given project code should be mapped to one element
          in the funding_list. This needs to be reduced.

        Returns
        -------
        List[Funding]
          The reduced list. There should be one element per
          (project_code, grant_number)

        """
        funder_grant_to_investigators_map = {}
        updated_list = []
        for funding_info in funding_list:
            if isinstance(funding_info.funder, str):
                funder_name = funding_info.funder
            else:
                funder_name = funding_info.funder.name
            map_key = (funder_name, funding_info.grant_number)
            if funder_grant_to_investigators_map.get(map_key) is None:
                funder_grant_to_investigators_map[map_key] = set(
                    [f.strip() for f in funding_info.fundee.split(",")]
                )
            else:
                og_fundee = funder_grant_to_investigators_map.get(map_key)
                new_fundee = set(
                    [f.strip() for f in funding_info.fundee.split(",")]
                )
                funder_grant_to_investigators_map[map_key] = og_fundee.union(
                    new_fundee
                )
        for (
            funder_grant_key,
            fundees,
        ) in funder_grant_to_investigators_map.items():
            funder_name = funder_grant_key[0]
            grant_number = funder_grant_key[1]
            # The lists are small enough that it is probably okay to sort the
            # fundees alphabetically for more consistent outputs
            fundee = None if fundees is None else ",".join(sorted(fundees))
            try:
                updated_funding = Funding(
                    funder=self._parse_institution(funder_name),
                    grant_number=grant_number,
                    fundee=fundee,
                )
            except ValidationError:
                updated_funding = Funding.model_construct(
                    funder=self._parse_institution(funder_name),
                    grant_number=grant_number,
                    fundee=fundee,
                )
            updated_list.append(updated_funding)
        return updated_list

    def _get_funding_list(self, project_code: str) -> List[Funding]:
        """
        Return a list of Funding information for a give project code.
        Parameters
        ----------
        project_code : str
          The project code that the user inputs.

        Returns
        -------
        List[Funding]
          A list of Funding models. They might not necessarily pass validation
          checks.

        """
        rows_associated_with_project_code: List[Funding] = []
        for row in self.model.rows:
            opt_funding: Optional[Funding] = self._map_row_to_funding(
                row=row, input_project_code=project_code
            )
            if opt_funding is not None:
                rows_associated_with_project_code.append(opt_funding)
        consolidated_list = self._reduce_funding_list(
            rows_associated_with_project_code
        )
        return consolidated_list

    def get_model_response(self, project_code: str) -> ModelResponse:
        """
        Return a ModelResponse for a given project code.
        Parameters
        ----------
        project_code : str
          The project code that the user inputs.

        Returns
        -------
        ModelResponse
          Will either be an internal server error response or a database
          responded response. Validation checks are performed downstream.

        """
        try:
            funding_list = self._get_funding_list(project_code=project_code)
            return ModelResponse(
                aind_models=funding_list, status_code=StatusCodes.DB_RESPONDED
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()