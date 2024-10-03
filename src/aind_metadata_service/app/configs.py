from pydantic_settings import BaseSettings
from aind_metadata_service.backends.labtracks.configs import (
    Settings as LabTracksSettings,
)


class AppSettings(BaseSettings):
    """App configuration"""

    lab_tracks_settings: LabTracksSettings
