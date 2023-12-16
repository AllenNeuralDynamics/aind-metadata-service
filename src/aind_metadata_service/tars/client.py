"""Module to instantiate a client to connect to TARS and retrieve data."""

import requests

from pydantic import BaseSettings, Field, SecretStr
from azure.identity import ClientSecretCredential
from aind_metadata_service.tars.query_builder import TarsQueries
from aind_metadata_service.tars.mapping import TarsResponseHandler


class AzureSettings(BaseSettings):
    """Configuration class. Mostly a wrapper around AzureAuth
    class constructor arguments."""

    tenant_id: str = Field(
        ..., description="The ID of the AllenInstituteB2C Azure tenant."
    )
    client_id: str = Field(
        ..., description="Client ID of the service account accessing resource."
    )
    client_secret: SecretStr = Field(
        ..., description="Secret used to access the account."
    )
    scope: str = Field(..., description="Scope")


class TarsClient:
    """Main client to connect to a TARS"""

    def __init__(self, azure_settings: AzureSettings, resource: str) -> None:
        """
        Class constructor
        Parameters
        ----------
        """
        self.credentials = ClientSecretCredential(
            tenant_id=azure_settings.tenant_id,
            client_id=azure_settings.client_id,
            client_secret=azure_settings.client_secret.get_secret_value(),
        )
        self.scope = azure_settings.scope
        self.resource = resource

    @property
    def get_access_token(self):
        """Retrieves Access Token"""
        token, exp = self.credentials.get_token(self.scope)
        return token

    @property
    def get_headers(self):
        return {"Authorization": f"Bearer {self.get_access_token}"}

    def get_injection_materials_info(self, prep_lot_number):
        """perform GET request"""
        headers = self.get_headers
        query = TarsQueries.prep_lot_from_number(
            resource=self.resource, prep_lot_number=prep_lot_number
        )
        response = requests.get(query, headers=headers)
        trh = TarsResponseHandler()
        injection_materials = trh.map_response_to_injection_materials(response)
        return injection_materials
