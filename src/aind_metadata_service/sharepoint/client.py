"""Module to create client to connect to sharepoint database"""

import logging
from typing import List, Optional

from aind_data_schema.core.procedures import Procedures
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.sharepoint.las2020.procedures import (
    LAS2020Procedures,
)
from aind_metadata_service.sharepoint.nsb2019.procedures import (
    NSB2019Procedures,
)
from aind_metadata_service.sharepoint.nsb2023.procedures import (
    NSB2023Procedures,
)


class SharepointSettings(BaseSettings):
    """Settings needed to connect to Sharepoint database"""

    nsb_sharepoint_url: str = Field(
        title="NSB Sharepoint URL",
        description="URL of the NSB sharepoint lists.",
    )
    las_sharepoint_url: str = Field(
        title="LAS Sharepoint URL",
        description="URL of the LAS sharepoint lists.",
    )
    nsb_2019_list: str = Field(
        default="SWR 2019-2022",
        title="NSB 2019 List",
        description="List name for Neurosurgery and Behavior 2019 database.",
    )
    nsb_2023_list: str = Field(
        default="SWR 2023-Present",
        title="NSB 2023 List",
        description="List name for Neurosurgery and Behavior 2023 database.",
    )
    las_2020_list: str = Field(
        default="NSPRequest2020",
        title="LAS 2020 List",
        description="List name for LAS Non-surgical Procedures 2020 database.",
    )
    sharepoint_user: str = Field(title="NSB User", description="NSB Username.")
    sharepoint_password: SecretStr = Field(
        title="NSB Password", description="Password."
    )


class SharePointClient:
    """This class contains the api to connect to SharePoint db."""

    def __init__(
        self,
        nsb_site_url: str,
        las_site_url: str,
        client_id: str,
        client_secret: str,
        nsb_2019_list_title: str,
        nsb_2023_list_title: str,
        las_2020_list_title: str,
    ) -> None:
        """
        Initialize a client
        Parameters
        ----------
        nsb_site_url : str
           sharepoint site url for nsb procedures
        las_site_url : str
           sharepoint site url for las procedures
        client_id : str
            username for principal account to access sharepoint
        client_secret : str
            password for principal account to access sharepoint
        nsb_2019_list_title : str
            Title for nsb 2019 list
        nsb_2023_list_title : str
            Title for nsb 2023 list
        las_2020_list_title : str
            Title for las 2020 list
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = ClientCredential(self.client_id, self.client_secret)
        self.nsb_site_url = nsb_site_url
        self.las_site_url = las_site_url
        self.nsb_2019_list_title = nsb_2019_list_title
        self.nsb_2023_list_title = nsb_2023_list_title
        self.las_2020_list_title = las_2020_list_title

    def get_client_context(self, site_url):
        """Construct client context with principal account"""
        return ClientContext(site_url).with_credentials(self.credentials)

    @classmethod
    def from_settings(cls, settings: SharepointSettings):
        """Construct client from settings object."""
        return cls(
            nsb_site_url=settings.nsb_sharepoint_url,
            las_site_url=settings.las_sharepoint_url,
            client_id=settings.sharepoint_user,
            client_secret=settings.sharepoint_password.get_secret_value(),
            nsb_2019_list_title=settings.nsb_2019_list,
            nsb_2023_list_title=settings.nsb_2023_list,
            las_2020_list_title=settings.las_2020_list,
        )

    def get_procedure_info(
        self, subject_id: str, list_title: str
    ) -> ModelResponse:
        """
        Primary interface. Maps a subject_id to a response.
        Parameters
        ----------
        subject_id : str
          ID of the subject being queried for.
        list_title: str
          Title of the sharepoint list to retrieve Procedures records

        Returns
        -------
        ModelResponse
          Either an internal_error response or a ModelResponse with a list
          of Procedures models

        """
        try:
            if list_title == self.nsb_2019_list_title:
                ctx = self.get_client_context(site_url=self.nsb_site_url)
                mapper = NSB2019Procedures()
            elif list_title == self.nsb_2023_list_title:
                ctx = self.get_client_context(site_url=self.nsb_site_url)
                mapper = NSB2023Procedures()
            elif list_title == self.las_2020_list_title:
                ctx = self.get_client_context(site_url=self.las_site_url)
                mapper = LAS2020Procedures()
            else:
                raise Exception(f"Unknown NSB Sharepoint List: {list_title}")
            subj_procedures = mapper.get_procedures_from_sharepoint(
                subject_id=subject_id,
                client_context=ctx,
                list_title=list_title,
            )
            procedures = self._handle_response_from_sharepoint(
                subject_id=subject_id, subject_procedures=subj_procedures
            )
            procedures = [] if procedures is None else [procedures]
            return ModelResponse(
                aind_models=procedures, status_code=StatusCodes.DB_RESPONDED
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    @staticmethod
    def _handle_response_from_sharepoint(
        subject_id: str, subject_procedures: Optional[list] = None
    ) -> Optional[Procedures]:
        """
        Maps the response from SharePoint into a Procedures model
        Parameters
        ----------
        subject_id : str
          ID of the subject being queried for.
        subject_procedures: Optional[list]
          An optional list of subject_procedures.

        Returns
        -------
        Optional[Procedures]
          A Procedures model if subject_procedures, else None.

        """
        if subject_procedures:
            procedures = Procedures.model_construct(subject_id=subject_id)
            procedures.subject_procedures = subject_procedures
            return procedures
        else:
            return None

    @staticmethod
    def _merge_procedures(
        left_procedures: List[Procedures], right_procedures: List[Procedures]
    ) -> List[Procedures]:
        """
        Merges two lists of Procedures. Given the way the lists are
        constructed, the length of the lists will either be 0 or 1.
        Parameters
        ----------
        left_procedures : List[Procedures]
        right_procedures : List[Procedures]

        Returns
        -------
        List[Procedures]
          Single model with the subject_procedures merged from both lists.

        """
        if len(left_procedures) == 0:
            return right_procedures
        elif len(right_procedures) == 0:
            return left_procedures
        else:
            subject_id = left_procedures[0].subject_id
            new_subject_procedures = (
                left_procedures[0].subject_procedures
                + right_procedures[0].subject_procedures
            )
            new_specimen_procedures = (
                left_procedures[0].specimen_procedures
                + right_procedures[0].specimen_procedures
            )
            return [
                Procedures.model_construct(
                    subject_id=subject_id,
                    subject_procedures=new_subject_procedures,
                    specimen_procedures=new_specimen_procedures,
                )
            ]

    def _merge_two_responses(
        self,
        left_model_response: ModelResponse[Procedures],
        right_model_response: ModelResponse[Procedures],
    ) -> ModelResponse[Procedures]:
        """
        Merges two ModelResponses of Procedures type.
        Parameters
        ----------
        left_model_response : ModelResponse[Procedures]
        right_model_response : ModelResponse[Procedures]

        Returns
        -------
        ModelResponse[Procedures]
          A merged response.

        """
        if (
            left_model_response.status_code.value >= 500
            and right_model_response.status_code.value >= 500
        ):
            return ModelResponse.internal_server_error_response()
        elif (
            left_model_response.status_code == StatusCodes.DB_RESPONDED
            and right_model_response.status_code.value >= 500
        ):
            return ModelResponse(
                aind_models=left_model_response.aind_models,
                status_code=StatusCodes.MULTI_STATUS,
                message=(
                    "There was an error retrieving records from one or more "
                    "of the databases."
                ),
            )
        elif (
            left_model_response.status_code.value >= 500
            and right_model_response.status_code == StatusCodes.DB_RESPONDED
        ):
            return ModelResponse(
                aind_models=right_model_response.aind_models,
                status_code=StatusCodes.MULTI_STATUS,
                message=(
                    "There was an error retrieving records from one or more "
                    "of the databases."
                ),
            )
        else:
            left_procedures: List[Procedures] = left_model_response.aind_models
            right_procedures: List[Procedures] = (
                right_model_response.aind_models
            )
            procedures = self._merge_procedures(
                left_procedures=left_procedures,
                right_procedures=right_procedures,
            )
            if (
                left_model_response.status_code == StatusCodes.MULTI_STATUS
                or right_model_response.status_code == StatusCodes.MULTI_STATUS
            ):
                return ModelResponse(
                    aind_models=procedures,
                    status_code=StatusCodes.MULTI_STATUS,
                    message=(
                        "There was an error retrieving records from one or "
                        "more of the databases."
                    ),
                )
            else:
                return ModelResponse(
                    aind_models=procedures,
                    status_code=StatusCodes.DB_RESPONDED,
                )

    def merge_responses(
        self, model_responses: List[ModelResponse[Procedures]]
    ) -> ModelResponse[Procedures]:
        """
        Merges a list of ModelResponses into a single ModelResponse using a
        left-scan operation.
        Parameters
        ----------
        model_responses : List[ModelResponse[Procedures]]

        Returns
        -------
        ModelResponse[Procedures]

        """
        if len(model_responses) == 0:
            return ModelResponse.internal_server_error_response()
        else:
            model_response = model_responses[0]
            for next_response in model_responses[1:]:
                model_response = self._merge_two_responses(
                    model_response, next_response
                )
            return model_response
