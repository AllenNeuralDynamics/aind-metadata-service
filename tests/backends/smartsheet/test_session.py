"""Tests session module"""

import pytest
from aind_smartsheet_api.client import SmartsheetClient, SmartsheetSettings

from aind_metadata_service.backends.smartsheet.session import get_session


class TestSession:
    """Test methods in Session Class"""

    def test_get_session(self):
        """Tests get_session method"""

        session = next(get_session())
        expected_session = SmartsheetClient(
            smartsheet_settings=SmartsheetSettings(
                access_token="abc-123", user_agent="some_user_agent"
            )
        )
        assert (
            expected_session.smartsheet_settings == session.smartsheet_settings
        )


if __name__ == "__main__":
    pytest.main([__file__])
