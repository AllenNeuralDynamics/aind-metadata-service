"""Module to instantiate a client to connect to TARS and retrieve data."""

import requests
from azure.identity import ClientSecretCredential
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


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
        azure_settings: AzureSettings
            Settings to define Azure ClientSecretCredential
        resource: str
            URL resource to query
        """
        self.credentials = ClientSecretCredential(
            tenant_id=azure_settings.tenant_id,
            client_id=azure_settings.client_id,
            client_secret=azure_settings.client_secret.get_secret_value(),
        )
        self.scope = azure_settings.scope
        self.resource = resource

    @property
    def _access_token(self):
        """Retrieves Access Token"""
        token, exp = self.credentials.get_token(self.scope)
        return token

    @property
    def _headers(self):
        """Builds headers for GET request."""
        return {"Authorization": f"Bearer {self._access_token}"}

    def get_prep_lot_response(
        self, prep_lot_number: str
    ) -> requests.models.Response:
        """
        Retrieves viral prep lot response from TARS.
        Parameters
        ----------
        prep_lot_number: str
           Prep lot number used to query ViralPrepLot endpoint.
        """
        headers = self._headers
        query = (
            f"{self.resource}/api/v1/ViralPrepLots"
            f"?order=1&orderBy=id"
            f"&searchFields=lot"
            f"&search={prep_lot_number}"
        )
        response = requests.get(query, headers=headers)
        return response
