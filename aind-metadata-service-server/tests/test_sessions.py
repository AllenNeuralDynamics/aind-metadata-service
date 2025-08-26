"""Tests session module"""

import pytest

from aind_metadata_service_server.sessions import (
    get_aind_data_schema_v1_session,
)


class TestSession:
    """Test methods in Session Class"""

    @pytest.mark.asyncio
    async def test_get_aind_data_schema_v1_session(self):
        """Tests get_session method"""
        session = await get_aind_data_schema_v1_session().__anext__()
        base_url = str(session.base_url)
        assert "http://example.com/v1/" == base_url


if __name__ == "__main__":
    pytest.main([__file__])
