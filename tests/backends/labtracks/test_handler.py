import pytest

from aind_metadata_service.backends.labtracks.handler import SessionHandler


class Test:

    def test_constructor(self, get_session):
        session_handler = SessionHandler(get_session)
        assert session_handler is not None

    def test_get_subject_value(self, get_session, test_subject):
        session_handler = SessionHandler(get_session)
        subject = session_handler.get_subject_view(subject_id="632269")
        assert test_subject == subject[0]


if __name__ == "__main__":
    pytest.main([__file__])
