"""Module to handle constructing TARS client."""

import requests

# from aind_metadata_service.backends.smartsheet.configs import get_settings

# Construct a Settings. Can be set via env vars or aws param store.
# settings = get_settings()


def get_session():
    """Yield a session object. This will automatically close the session when
    finished."""
    session = requests.Session()
    yield session
