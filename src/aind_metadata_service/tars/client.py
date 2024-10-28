"""Module to instantiate a client to connect to TARS and retrieve data."""

import logging
from typing import List, Optional

import requests
from azure.identity import ClientSecretCredential
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.tars.mapping import TarsResponseHandler


class AzureSettings(BaseSettings):
    """Configuration class. Mostly a wrapper around AzureAuth
    class constructor arguments."""

    model_config = SettingsConfigDict(env_prefix="TARS_")

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
    resource: str = Field(..., description="Resource")


class TarsClient:
    """Main client to connect to a TARS"""

    def __init__(self, azure_settings: AzureSettings) -> None:
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
        self.resource = azure_settings.resource

    @property
    def _access_token(self):
        """Retrieves Access Token"""
        token, exp = self.credentials.get_token(self.scope)
        return token

    @property
    def _headers(self):
        """Builds headers for GET request."""
        return {"Authorization": f"Bearer {self._access_token}"}

    def _get_prep_lot_response(
        self, prep_lot_number: str
    ) -> Optional[requests.models.Response]:
        """
        Retrieves viral prep lot response from TARS. Returns
        all lots that contain prep_lot_number.
        Parameters
        ----------
        prep_lot_number: str
           Prep lot number used to query ViralPrepLot endpoint.
        """
        headers = self._headers
        if prep_lot_number and len(prep_lot_number) > 0:
            query = (
                f"{self.resource}/api/v1/ViralPrepLots"
                f"?order=1&orderBy=id"
                f"&searchFields=lot"
                f"&search={prep_lot_number}"
            )
            return requests.get(query, headers=headers)
        else:
            raise ValueError("Please input a valid prep lot number.")

    @staticmethod
    def _filter_prep_lot_response(
        prep_lot_number: str, response: requests.models.Response
    ) -> Optional[List]:
        """
        Filters response from TARS for exact match.
        Parameters
        ----------
        prep_lot_number: str
           Prep lot number used to query ViralPrepLot endpoint.
        response : requests.models.Response
           Raw Response from ViralPrepLot endpoint
        """
        data = response.json()["data"]
        filtered_data = [lot for lot in data if lot["lot"] == prep_lot_number]
        if not filtered_data:
            raise ValueError(f"No data found for {prep_lot_number}")
        return filtered_data

    def _get_molecules_response(
        self, plasmid_name: str
    ) -> requests.models.Response:
        """
        Retrieves molecules from TARS.
        Parameters
        ----------
        plasmid_name: str
           Plasmid name used to query Molecules endpoint.
        """
        headers = self._headers
        query = (
            f"{self.resource}/api/v1/Molecules"
            f"?order=1&orderBy=id"
            f"&searchFields=name"
            f"&search={plasmid_name}"
        )
        response = requests.get(query, headers=headers)
        return response

    def get_injection_materials_info(
        self, prep_lot_number: str
    ) -> ModelResponse:
        """
        Fetches response from TARS and then handles mapping to
        create a ModelResponse. Either returns a DB_Responded
        ModelResponse or an Error ModelResponse.
        """
        try:
            response = self._get_prep_lot_response(prep_lot_number)
            data = self._filter_prep_lot_response(prep_lot_number, response)
            trh = TarsResponseHandler()
            injection_materials = []

            for lot in data:
                viral_prep_aliases = trh.map_virus_aliases(
                    aliases=lot["viralPrep"]["virus"]["aliases"]
                )
                if (
                    viral_prep_aliases.plasmid_name
                    and viral_prep_aliases.full_genome_name is None
                ):
                    # check molecular registry for full genome name
                    molecule_response = self._get_molecules_response(
                        viral_prep_aliases.plasmid_name
                    )
                    viral_prep_aliases.full_genome_name = (
                        trh.map_full_genome_name(
                            molecule_response, viral_prep_aliases.plasmid_name
                        )
                    )
                injection_material = trh.map_lot_to_injection_material(
                    viral_prep_lot=lot, viral_prep_aliases=viral_prep_aliases
                )
                injection_materials.append(injection_material)
            return ModelResponse(
                aind_models=injection_materials,
                status_code=StatusCodes.DB_RESPONDED,
            )
        # handles connection error
        except ConnectionError as e:
            logging.error(repr(e))
            return ModelResponse.connection_error_response()
        # handles if no data is found
        except ValueError as e:
            logging.error(repr(e))
            return ModelResponse.no_data_found_error_response()
        # handles all other errors
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()
