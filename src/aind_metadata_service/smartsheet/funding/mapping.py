"""Module that handles the methods to map the SmartSheet response to the
aind-data-schema Funding model."""

import logging
from typing import List, Optional, Union

from aind_data_schema_models.organizations import Organization
from pydantic import ValidationError
from starlette.responses import JSONResponse

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.models import FundingInformation
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.funding.models import FundingColumnNames
from aind_metadata_service.smartsheet.mapper import SmartSheetMapper
from aind_metadata_service.smartsheet.models import SheetRow


class FundingMapper(SmartSheetMapper):
    """Primary class to handle mapping data models and returning a response"""

    @staticmethod
    def _parse_institution(
        input_name: Optional[str],
    ) -> Optional[Union[Organization, str]]:
        """
        Generate Institution from string
        Parameters
        ----------
        input_name : Optional[str]
          Institution name

        Returns
        -------
        Optional[Union[Institution, str]]
          Either an Institution parsed from the name. If the Institution can't
          be generated from the name, then it returns the input name.

        """
        if input_name is None:
            return None
        elif Organization().name_map.get(input_name) is not None:
            return Organization().name_map.get(input_name)
        elif Organization().abbreviation_map.get(input_name) is not None:
            return Organization().abbreviation_map.get(input_name)
        else:
            return input_name

    def _map_row_to_funding(
        self, row: SheetRow, input_project_name: str
    ) -> Optional[FundingInformation]:
        """
        Map a row to an optional funding model.
        Parameters
        ----------
        row : SheetRow
        input_project_name : str
          The project name the user inputs

        Returns
        -------
        Union[Funding, None]
          None if the project name in the row doesn't match the
          input_project_name. Otherwise, will try to return a valid Funding
          model. If there is some data entry mistake, then it will return a
          Funding model as good as it can.

        """

        row_dict = self.map_row_to_dict(row)
        top_project_name = row_dict.get(FundingColumnNames.PROJECT_NAME)
        subproject_name = row_dict.get(FundingColumnNames.SUBPROJECT)
        if subproject_name is not None:
            project_name = f"{top_project_name} - {subproject_name}"
        else:
            project_name = top_project_name
        grant_number = row_dict.get(FundingColumnNames.GRANT_NUMBER)
        institution_value = row_dict.get(
            FundingColumnNames.FUNDING_INSTITUTION
        )
        funder = self._parse_institution(institution_value)
        investigators = row_dict.get(FundingColumnNames.INVESTIGATORS)
        fundees = row_dict.get(FundingColumnNames.FUNDEES)
        if (
            input_project_name != project_name
            and input_project_name != top_project_name
        ):
            return None
        elif (
            funder is None
            and grant_number is None
            and investigators is None
            and fundees is None
        ):
            return None
        else:
            try:
                return FundingInformation(
                    funder=funder,
                    grant_number=grant_number,
                    fundee=fundees,
                    investigators=investigators,
                )
            except ValidationError:
                return FundingInformation.model_construct(
                    funder=funder,
                    grant_number=grant_number,
                    fundee=fundees,
                    investigators=investigators,
                )

    def _get_funding_list(self, project_name: str) -> List[FundingInformation]:
        """
        Return a list of Funding information for a give project code.
        Parameters
        ----------
        project_name : str
          The project name that the user inputs.

        Returns
        -------
        List[Funding]
          A list of Funding models. They might not necessarily pass validation
          checks.
        """
        rows_associated_with_project_name: List[FundingInformation] = []
        for row in self.model.rows:
            opt_funding: Optional[FundingInformation] = (
                self._map_row_to_funding(
                    row=row, input_project_name=project_name
                )
            )
            if opt_funding is not None:
                rows_associated_with_project_name.append(opt_funding)
        return rows_associated_with_project_name

    def _get_model_response(self) -> ModelResponse:
        """
        Return a ModelResponse
        Returns
        -------
        ModelResponse
          Will either be an internal server error response or a database
          responded response. Validation checks are performed downstream.

        """
        try:
            funding_list = self._get_funding_list(project_name=self.input_id)
            return ModelResponse(
                aind_models=funding_list, status_code=StatusCodes.DB_RESPONDED
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    def get_project_names(self) -> JSONResponse:
        """Get list of project names from funding sheet"""
        try:
            project_names = set()
            for row in self.model.rows:
                row_dict = self.map_row_to_dict(row)
                project_name = row_dict.get(FundingColumnNames.PROJECT_NAME)
                subproject_name = row_dict.get(FundingColumnNames.SUBPROJECT)
                if project_name is not None and subproject_name is None:
                    project_names.add(project_name)
                elif project_name is not None and subproject_name is not None:
                    # Support legacy input.
                    project_names.add(project_name)
                    project_names.add(f"{project_name} - {subproject_name}")
            return JSONResponse(
                status_code=200,
                content=(
                    {"message": "Success", "data": sorted(list(project_names))}
                ),
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content=({"message": f"Error: {e}", "data": None}),
            )
