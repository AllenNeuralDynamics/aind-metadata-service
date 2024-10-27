"""Tests for handler module"""

import pytest

from aind_metadata_service.backends.labtracks.handler import SessionHandler


class TestHandler:
    """Test SessionHandler"""

    def test_constructor(self, get_lab_tracks_session):
        """Tests class can be constructed."""
        session_handler = SessionHandler(get_lab_tracks_session)
        assert session_handler is not None

    def test_get_subject_value(
        self, get_lab_tracks_session, test_lab_tracks_subject
    ):
        """Tests subject view is returned correctly."""
        session_handler = SessionHandler(get_lab_tracks_session)
        subject = session_handler.get_subject_view(subject_id="632269")
        assert test_lab_tracks_subject == subject[0]


if __name__ == "__main__":
    pytest.main([__file__])
