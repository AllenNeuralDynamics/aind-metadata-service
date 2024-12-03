"""Module to handle constructing TARS client."""

import requests


def get_session():
    """Yield a session object. This will automatically close the session when
    finished."""
    session = requests.Session()
    yield session
