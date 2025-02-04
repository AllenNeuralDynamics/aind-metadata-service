"""Module to handle SLIMS session"""

from aind_slims_api.core import SlimsClient

from aind_metadata_service.backends.slims.configs import get_settings

# Construct a Settings. Can be set via env vars or aws param store.
settings = get_settings()


def get_session():
    """Yield a session object. This will automatically close the session when
    finished."""
    session = SlimsClient(
        url=settings.url,
        username=settings.username,
        password=settings.password.get_secret_value(),
    )
    yield session
