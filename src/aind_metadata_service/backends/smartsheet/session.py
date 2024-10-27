"""Module to handle constructing Smartsheet client."""

from aind_smartsheet_api.client import SmartsheetClient

from aind_metadata_service.backends.smartsheet.configs import get_settings

# Construct a Settings. Can be set via env vars or aws param store.
settings = get_settings()


def get_session():
    """Yield a session object. This will automatically close the session when
    finished."""
    session = SmartsheetClient(smartsheet_settings=settings.client_settings)
    yield session
