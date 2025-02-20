"""Module to create client to connect to sharepoint database"""

import logging
import requests
from typing import List, Optional

from aind_data_schema.core.procedures import Procedures
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.sharepoint.las2020.procedures import LAS2020Procedures
from aind_metadata_service.sharepoint.nsb2019.procedures import NSB2019Procedures
from aind_metadata_service.sharepoint.nsb2023.procedures import NSB2023Procedures

class SharepointSettings(BaseSettings):
    aind_site_id: str = Field(
        title="AIND Site ID",
        description="Site ID of the AIND SharePoint site.",
    )
    las_site_id: str = Field(
        title="LAS Site ID",
        description="Site ID of the LAS SharePoint site.",
    )
    nsb_2019_list_id: str = Field(
        title="NSB 2019 List ID",
        description="List ID for NSB 2019 procedures.",
    )
    nsb_2023_list_id: str = Field(
        title="NSB 2023 List ID",
        description="List ID for NSB 2023 procedures.",
    )
    las_2020_list_id: str = Field(
        title="LAS 2020 List ID",
        description="List ID for LAS 2020 procedures.",
    )
    client_id: str = Field(
        title="Client ID",
        description="Client ID for the principal account.",
    )
    client_secret: SecretStr = Field(
        title="Client Secret",
        description="Client Secret for the principal account.",
    )
    tenant_id: str = Field(
        title="Tenant ID",
        description="Tenant ID for the principal account.",
    )

    class Config:
        env_prefix = "SHAREPOINT_"
        extra = "forbid"


class SharePointClient:
    GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

    def __init__(
        self,
        aind_site_id: str,
        las_site_id: str,
        nsb_2019_list_id: str,
        nsb_2023_list_id: str,
        las_2020_list_id: str,
        client_id: str,
        client_secret: SecretStr,
        tenant_id: str,
    ) -> None:
        self.aind_site_id = aind_site_id
        self.las_site_id = las_site_id
        self.nsb_2019_list_id = nsb_2019_list_id
        self.nsb_2023_list_id = nsb_2023_list_id
        self.las_2020_list_id = las_2020_list_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self._access_token: Optional[str] = None

    @classmethod
    def from_settings(cls, settings: SharepointSettings):
        """
        Create a SharePointClient instance from a SharepointSettings object.
        """
        return cls(
            aind_site_id=settings.aind_site_id,
            las_site_id=settings.las_site_id,
            nsb_2019_list_id=settings.nsb_2019_list_id,
            nsb_2023_list_id=settings.nsb_2023_list_id,
            las_2020_list_id=settings.las_2020_list_id,
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            tenant_id=settings.tenant_id,
        )
    
    def get_access_token(self) -> str:
        """Obtain an OAuth access token from Microsoft Identity Platform."""
        if self._access_token:
            return self._access_token
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret.get_secret_value(),
            "scope": "https://graph.microsoft.com/.default",
        }
        try:
            response = requests.post(self.token_url, data=payload)
            response.raise_for_status()
            self._access_token = response.json().get("access_token")
            return self._access_token
        except requests.exceptions.RequestException as e:
            logging.error(f"Error obtaining access token: {e}")
            raise RuntimeError("Failed to authenticate with SharePoint.")

    def _get_headers(self) -> dict:
        """Construct the request headers using the access token."""
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _fetch_list_items(self, site_id: str, list_id: str) -> dict:
        """
        Fetch items from a SharePoint list using the Graph API.
        Adjust the query parameters as needed.
        """
        url = f"{self.GRAPH_API_URL}/sites/{site_id}/lists/{list_id}/items?expand=fields"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching list items from list {list_id}: {e}")
            raise RuntimeError(f"Failed to fetch list items for list {list_id}.")

    def get_procedure_info(self, subject_id: str, list_id: str) -> ModelResponse:
        """
        Retrieve procedure info from the specified SharePoint list based on subject_id.
        Chooses the proper mapper depending on which list is queried.
        """
        try:
            if list_id == self.nsb_2019_list_id:
                raw_data = self._fetch_list_items(site_id=self.aind_site_id, list_id=list_id)
                mapper = NSB2019Procedures()
            elif list_id == self.nsb_2023_list_id:
                raw_data = self._fetch_list_items(site_id=self.aind_site_id, list_id=list_id)
                mapper = NSB2023Procedures()
            elif list_id == self.las_2020_list_id:
                raw_data = self._fetch_list_items(site_id=self.las_site_id, list_id=list_id)
                mapper = LAS2020Procedures()
            else:
                raise Exception(f"Unknown SharePoint List: {list_id}")

            # Note: The mapper should be adapted to accept the raw JSON data.
            subject_procedures = mapper.get_procedures_from_sharepoint(
                subject_id=subject_id, raw_data=raw_data
            )
            procedures = self._handle_response_from_sharepoint(
                subject_id=subject_id, subject_procedures=subject_procedures
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
        """Map the raw procedures response into a Procedures model."""
        if subject_procedures:
            procedures = Procedures.model_construct(subject_id=subject_id)
            procedures.subject_procedures = subject_procedures
            return procedures
        else:
            return None

    def _merge_procedures(
        self, left_procedures: List[Procedures], right_procedures: List[Procedures]
    ) -> List[Procedures]:
        """Merge two lists of Procedures."""
        if not left_procedures:
            return right_procedures
        elif not right_procedures:
            return left_procedures
        else:
            subject_id = left_procedures[0].subject_id
            new_subject_procedures = (
                left_procedures[0].subject_procedures + right_procedures[0].subject_procedures
            )
            new_specimen_procedures = (
                left_procedures[0].specimen_procedures + right_procedures[0].specimen_procedures
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
        """Merge two ModelResponse objects containing Procedures."""
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
            right_procedures: List[Procedures] = right_model_response.aind_models
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
        Merge a list of ModelResponses into a single response.
        """
        if not model_responses:
            return ModelResponse.internal_server_error_response()
        model_response = model_responses[0]
        for next_response in model_responses[1:]:
            model_response = self._merge_two_responses(model_response, next_response)
        return model_response
