"""Module to instantiate a client to connect to TARS and retrieve data."""

import requests

from pydantic import BaseSettings, Field, SecretStr
from azure.identity import ClientSecretCredential
from enum import Enum


class APICalls(Enum):
    """Enum of different API calls for TARS"""
    REFERENCE_GENOMES = "/api/v1/ReferenceGenomes"
    TITER_IMPORTS = "/api/v1/TiterImports"
    TITER_TYPES = "/api/v1/TiterTypes"
    VIRAL_PREP_IMPORTS = "/api/v1/ViralPrepImports"
    VIRAL_PREP_LOTS = "/api/v1/ViralPrepLots"
    VIRAL_PREPS = "/api/v1/ViralPreps"
    VIRAL_PREP_TYPES = "/api/v1/ViralPrepTypes"
    DEFAULT_ORDER = "order=1&orderBy=id"


class AzureSettings(BaseSettings):
    """Configuration class. Mostly a wrapper around AzureAuth
    class constructor arguments."""

    tenant_id: str = Field(
        ...,
        description="The ID of the AllenInstituteB2C Azure tenant."
    )
    client_id: str = Field(
        ...,
        description="Client ID of the service account accessing resource."
    )
    client_secret: SecretStr = Field(
        ...,
        description="Secret used to access the account."
    )
    scope: str = Field(
        ...,
        description="Scope"
    )


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
            client_secret=azure_settings.client_secret.get_secret_value()
        )
        self.scope = azure_settings.scope
        self.resource = resource

    @property
    def get_access_token(self):
        """Retrieves Access Token"""
        credential = self.credentials
        token, exp = credential.get_token(self.scope)
        return token

    @property
    def get_headers(self):
        return f"Authorization: Bearer {self.get_access_token}"

    def get_injection_materials_info(self, viral_prep_number):
        """Retrieve UUID for TARS with prep lot number"""
        request_str = self.resource + APICalls.VIRAL_PREP_LOTS.value
        search_str = f"?order=1&orderBy=ViralPrepLots.lot&searchFields=lot&search={viral_prep_number}"
        request = requests.get(request_str + search_str)
        data = request.json()['data'][0]
        # NOTE: there should only be one data
        prep_date = data['datePrepped'] #convert to date
        viral_prep_type = data['viralPrep']['viralPrepType']['name'] # split into prep_type and prep_protocol


class ViralPrepTypes(Enum):
    """"""
    CRUDE_SOP = "Crude-SOP#VC002"
    PURIFIED_SOP = "Purified-SOP#VC003"
    CRUDE_HGT = "Crude-HGT"
    RABIES_SOP = "Rabies-SOP#VC001"
    CRUDE_PHP_SOP = "CrudePHPeB-SOP#VC004"
    CRUDE_MGT2 = "Crude-MGT#2.0"
    CRUDE_MGT1 = "Crude-MGT#1.0"
    PURIFIED_MGT1 = "Purified-MGT#1.0"
    PHP_SOP_UW = "PHPeB-SOP-UW"
    CRUDE_HGT1 = "Crude-HGT#1.0"
    VTC_AAV1 = "VTC-AAV1"
    UNKNOWN = "Unknown"
    IODIXANOL = "Iodixanol gradient purification (large scale preps)"


class TarsResponseHandler:
    """This class will contain methods to handle the response from TARS"""


