"""Module for settings to connect to TARS backend"""

from azure.identity import ClientSecretCredential
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings needed to connect to LabTracks Database"""

    # noinspection SpellCheckingInspection
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

    def get_bearer_token(self):
        """Retrieves Access Token"""
        credentials = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret.get_secret_value(),
        )
        token, exp = credentials.get_token(self.scope)
        return token, exp


def get_settings() -> Settings:
    """Utility method to return a settings object."""
    return Settings()
