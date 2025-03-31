"""Module to create client to connect to sharepoint database"""

import json
import logging
import os
from typing import Iterator, List, Optional, Union

import requests
from aind_data_schema.core.procedures import Procedures, Surgery
from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict
from requests import Session

from aind_metadata_service.models import IntendedMeasurementInformation
from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.settings import ParameterStoreBaseSettings
from aind_metadata_service.sharepoint.las2020 import LASList, MappedLASList
from aind_metadata_service.sharepoint.nsb2019 import (
    MappedNSB2019List,
    NSB2019List,
)
from aind_metadata_service.sharepoint.nsb2023 import (
    MappedNSB2023List,
    NSB2023List,
)


class SharepointSettings(ParameterStoreBaseSettings):
    """Settings needed to connect to Sharepoint database"""

    model_config = SettingsConfigDict(
        env_prefix="SHAREPOINT_",
        extra="ignore",
        aws_param_store_name=os.getenv("AWS_PARAM_STORE_NAME"),
    )

    aind_site_id: str = Field(
        title="AIND Site ID",
        description="Site ID of the AIND SharePoint site.",
    )
    las_site_id: str = Field(
        title="LAS Site ID",
        description="Site ID of the LAS SharePoint site.",
    )
    nsb_2019_list_id: str = Field(
        title="NSB 2019-2022 Archive List ID",
        description="List ID for NSB 2019-2022 procedures.",
    )
    nsb_2023_list_id: str = Field(
        title="NSB 2023-2024 Archive List ID",
        description="List ID for NSB 2023-2024 Archive procedures.",
    )
    nsb_present_list_id: str = Field(
        title="NSB 2023-Present List ID",
        description="List ID for NSB Present procedures.",
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
    graph_api_url: str = Field(
        title="Graph API URL",
        description="URL for the Microsoft Graph API.",
        default="https://graph.microsoft.com/v1.0",
    )
    scope: str = Field(
        title="Scope",
        description="Scope for the Microsoft Graph API.",
        default="https://graph.microsoft.com/.default",
    )
    token_url: Optional[str] = Field(
        None,
        title="Token URL",
        description="URL for the Microsoft Identity Platform.",
    )

    @field_validator("token_url", mode="before")
    def set_token_url(cls, v, info):
        """Sets token_url from tenant_id if not provided."""
        if v is not None:
            return v
        tenant_id = info.data.get("tenant_id")
        if not tenant_id:
            raise ValueError(
                "tenant_id must be provided to generate token_url"
            )
        return (
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        )


class SharePointClient:
    """This class contains the API to connect to Sharepoint Database."""

    def __init__(
        self,
        aind_site_id: str,
        las_site_id: str,
        nsb_2019_list_id: str,
        nsb_2023_list_id: str,
        nsb_present_list_id: str,
        las_2020_list_id: str,
        client_id: str,
        client_secret: SecretStr,
        tenant_id: str,
        graph_api_url: str,
        scope: str,
        token_url: str,
    ) -> None:
        """
        Initailize the SharePointClient with the required parameters.
        Parameters
        ----------
        aind_site_id : str
            Sharepoint Site ID for AIND Domain
        las_site_id : str
            Sharepoint Site ID for LAS Domain
        nsb_2019_list_id : str
            List ID for NSB 2019-2022 procedures
        nsb_2023_list_id : str
            List ID for NSB 2023-2024 Archive procedures
        nsb_present_list_id : str
            List ID for NSB 2023-Present procedures
        las_2020_list_id : str
            List ID for LAS 2020 procedures
        client_id : str
            Client ID for the principal account
        client_secret : SecretStr
            Client Secret for the principal account
        tenant_id : str
            Tenant ID for the principal account
        graph_api_url : str
            URL for the Microsoft Graph API
        scope : str
            Scope for the Microsoft Graph API
        token_url : str
            URL for the Microsoft Identity
        """
        self.aind_site_id = aind_site_id
        self.las_site_id = las_site_id
        self.nsb_2019_list_id = nsb_2019_list_id
        self.nsb_2023_list_id = nsb_2023_list_id
        self.nsb_present_list_id = nsb_present_list_id
        self.las_2020_list_id = las_2020_list_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.token_url = token_url
        self.graph_api_url = graph_api_url
        self.scope = scope
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
            nsb_present_list_id=settings.nsb_present_list_id,
            las_2020_list_id=settings.las_2020_list_id,
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            tenant_id=settings.tenant_id,
            graph_api_url=settings.graph_api_url,
            scope=settings.scope,
            token_url=settings.token_url,
        )

    def get_access_token(self) -> str:
        """Obtain an OAuth access token from Microsoft Identity Platform."""
        if self._access_token:
            return self._access_token
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret.get_secret_value(),
            "scope": self.scope,
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
            "Content-Type": "application/json",
        }

    @staticmethod
    def _paginate(url: str, params: dict, session: Session) -> Iterator[dict]:
        """

        Parameters
        ----------
        url : str
        params : dict
        session : Session

        Returns
        -------
        Iterator[dict]

        """
        while True:
            response = session.get(url, params=params)
            response.raise_for_status()
            for result in response.json().get("value", []):
                yield result

            if not response.json().get("@odata.nextLink"):
                return

            url = response.json().get("@odata.nextLink")
            params = None

    def _fetch_all_list_items(
        self, site_id: str, list_id: str, subject_id: str
    ) -> list:
        """
        Fetch all items from a LAS SharePoint list using the Graph API.
        Implements pagination for large lists correctly. Filters by
        Retro-Orbital Injections.
        """
        url = f"{self.graph_api_url}/sites/{site_id}/lists/{list_id}/items"
        params = {
            "expand": "fields",
            "$filter": "fields/ReqPro1 eq 'Retro-Orbital Injection'",
        }
        headers = self._get_headers()
        all_items = []
        with Session() as session:
            session.headers.update(headers)
            paginator = self._paginate(url=url, params=params, session=session)
            for item in paginator:
                if subject_id in item.get("fields", dict()).get("Title", ""):
                    all_items.append(item)
        return all_items

    def _fetch_list_items(
        self, site_id: str, list_id: str, subject_id: str, subject_alias: str
    ) -> dict:
        """
        Fetch items from a SharePoint list using the Graph API.
        Handles simple filtering by subject_id.
        """
        params = {
            "expand": "fields",
            "$filter": f"fields/{subject_alias} eq '{subject_id}'",
        }
        try:
            response = requests.get(
                f"{self.graph_api_url}/sites/{site_id}/lists/{list_id}/items",
                headers=self._get_headers(),
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Error fetching list items from list {list_id}: {e}"
            )
            raise RuntimeError(
                f"Failed to fetch list items for list {list_id}."
            )

    def get_intended_measurement_info(self, subject_id: str):
        """
        Retrieve intended measurement info from NSB 2023-2024 Archive
        and NSB 2023-Present list by subject_id.
        """
        try:
            subject_alias = NSB2023List.model_fields.get(
                "lab_tracks_id1"
            ).alias
            measurements = []
            for list_id in [self.nsb_2023_list_id, self.nsb_present_list_id]:
                response = self._fetch_list_items(
                    site_id=self.aind_site_id,
                    list_id=list_id,
                    subject_id=subject_id,
                    subject_alias=subject_alias,
                )
                measurements.extend(
                    self._extract_intended_measurements_from_response(response)
                )
            unique_measurements = self._handle_duplicates(measurements)

            return ModelResponse(
                aind_models=unique_measurements,
                status_code=StatusCodes.DB_RESPONDED,
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    @staticmethod
    def _extract_intended_measurements_from_response(
        response: dict,
    ) -> List[IntendedMeasurementInformation]:
        """
        Extract intended measurements from a raw Graph API response
        using the NSB 2023 model and mapper classes.
        """
        return [
            measurement
            for item in response.get("value", [])
            for measurement in MappedNSB2023List(
                NSB2023List.model_validate(item["fields"])
            ).get_intended_measurements()
        ]

    def get_procedure_info(
        self, subject_id: str, list_id: str
    ) -> ModelResponse:
        """
        Retrieve procedure info from specified SharePoint list by subject_id.
        Chooses the proper mapper depending on which list is queried.
        """
        try:
            if list_id == self.nsb_2019_list_id:
                logging.info(f"Pulling data from nsb 2019 for {subject_id}")
                subject_alias = NSB2019List.model_fields.get(
                    "lab_tracks_id"
                ).alias
                response = self._fetch_list_items(
                    site_id=self.aind_site_id,
                    list_id=list_id,
                    subject_id=subject_id,
                    subject_alias=subject_alias,
                )
                subj_procedures = self._extract_procedures_from_response(
                    response=response,
                    model_cls=NSB2019List,
                    mapper_cls=MappedNSB2019List,
                )
                logging.info(
                    f"Found {len(subj_procedures)} items from nsb 2019-2022"
                    f" for {subject_id}"
                )
            elif list_id == self.nsb_2023_list_id:
                logging.info(f"Pulling data from nsb 2023 for {subject_id}")
                subject_alias = NSB2023List.model_fields.get(
                    "lab_tracks_id1"
                ).alias
                response = self._fetch_list_items(
                    site_id=self.aind_site_id,
                    list_id=list_id,
                    subject_id=subject_id,
                    subject_alias=subject_alias,
                )
                subj_procedures = self._extract_procedures_from_response(
                    response=response,
                    model_cls=NSB2023List,
                    mapper_cls=MappedNSB2023List,
                )
                logging.info(
                    f"Found {len(subj_procedures)} items from nsb 2023-2024"
                    f" archive for {subject_id}"
                )
            elif list_id == self.nsb_present_list_id:
                # NSB Present List uses same schema as NSB 2023 List
                subject_alias = NSB2023List.model_fields.get(
                    "lab_tracks_id1"
                ).alias
                response = self._fetch_list_items(
                    site_id=self.aind_site_id,
                    list_id=list_id,
                    subject_id=subject_id,
                    subject_alias=subject_alias,
                )
                subj_procedures = self._extract_procedures_from_response(
                    response=response,
                    model_cls=NSB2023List,
                    mapper_cls=MappedNSB2023List,
                )
                logging.info(
                    f"Found {len(subj_procedures)} items from nsb 2023-present"
                    f" for {subject_id}"
                )
            elif list_id == self.las_2020_list_id:
                logging.info(f"Pulling data from LAS 2020 for {subject_id}")
                all_items = self._fetch_all_list_items(
                    site_id=self.las_site_id,
                    list_id=list_id,
                    subject_id=subject_id,
                )
                subj_procedures = self._extract_procedures_from_response(
                    response={"value": all_items},
                    model_cls=LASList,
                    mapper_cls=MappedLASList,
                    subject_id=subject_id,
                )
                logging.info(
                    f"Found {len(subj_procedures)} items from las 2020 for"
                    f" {subject_id}"
                )
            else:
                return ModelResponse.internal_server_error_response()
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
    def _extract_procedures_from_response(
        response: dict,
        model_cls: type,
        mapper_cls: type,
        subject_id: Optional[str] = None,
    ) -> List[Surgery]:
        """
        Extract procedures from a raw Graph API response using
        the provided model and mapper classes.
        """
        list_of_procedures = []
        for item in response.get("value", []):
            model = model_cls.model_validate(item["fields"])
            mapped_model = mapper_cls(model)
            if model_cls == LASList:
                procedure = mapped_model.get_procedure(subject_id)
                procedures = [procedure] if procedure else []
            else:
                procedures = mapped_model.get_procedure()
            list_of_procedures.extend(procedures)
        return list_of_procedures

    @staticmethod
    def _handle_duplicates(
        items: List[Union[dict, BaseModel]]
    ) -> List[Union[dict, BaseModel]]:
        """Remove duplicates from a list of dictionaries or pydantic models."""

        seen = set()
        unique = []

        for item in items:
            if isinstance(item, BaseModel):
                identifier = json.dumps(
                    item.model_dump(), sort_keys=True, default=str
                )
            elif isinstance(item, dict):
                identifier = json.dumps(item, sort_keys=True, default=str)
            else:
                raise TypeError(f"Unsupported item type: {type(item)}")

            if identifier not in seen:
                seen.add(identifier)
                unique.append(item)
            else:
                logging.info("Duplicate item found and removed.")

        return unique

    def _handle_response_from_sharepoint(
        self, subject_id: str, subject_procedures: Optional[list] = None
    ) -> Optional[Procedures]:
        """Map the raw procedures response into a Procedures model."""
        if subject_procedures:
            procedures = Procedures.model_construct(subject_id=subject_id)
            procedures.subject_procedures = subject_procedures
            return procedures
        else:
            return None

    def _merge_procedures(
        self,
        left_procedures: List[Procedures],
        right_procedures: List[Procedures],
    ) -> List[Procedures]:
        """Merge two lists of Procedures."""
        if not left_procedures:
            return right_procedures
        elif not right_procedures:
            return left_procedures
        else:
            subject_id = left_procedures[0].subject_id
            new_subject_procedures = (
                left_procedures[0].subject_procedures
                + right_procedures[0].subject_procedures
            )
            unique_subject_procedures = self._handle_duplicates(
                new_subject_procedures
            )
            new_specimen_procedures = (
                left_procedures[0].specimen_procedures
                + right_procedures[0].specimen_procedures
            )
            return [
                Procedures.model_construct(
                    subject_id=subject_id,
                    subject_procedures=unique_subject_procedures,
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
        Merge a list of ModelResponses into a single response.
        """
        if not model_responses:
            return ModelResponse.internal_server_error_response()
        model_response = model_responses[0]
        for next_response in model_responses[1:]:
            model_response = self._merge_two_responses(
                model_response, next_response
            )
        return model_response
