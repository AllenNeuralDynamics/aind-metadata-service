import unittest
from pathlib import Path
import os
import json
from aind_data_schema.core.session import Session
from aind_slims_api.operations.ecephys_session import EcephysSession as SlimsEcephysSession
from aind_metadata_service.slims.mapping import SlimsSessionMapper

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "resources" / "slims"
SLIMS_RESPONSE = RESOURCES_DIR / "slims_ecephys_session_response.json"
EXPECTED_SESSIONS = RESOURCES_DIR / "expected_ecephys_session.json"

class TestSlimsSessionMapper(unittest.TestCase):
    """Class to test methods of SLimsSessionMapper"""

    def setUp(self):
        """Sets up test class"""
        self.mapper = SlimsSessionMapper()
        with open(SLIMS_RESPONSE, "r") as file:
            slims_data = json.load(file)
        with open(EXPECTED_SESSIONS, encoding="utf-8") as f:
            expected_data = json.load(f)
        self.slims_sessions = SlimsEcephysSession.model_validate(slims_data)
        self.expected_session = expected_data

    def test_map_sessions(self):
        """Tests map sessions"""
        sessions = self.mapper.map_sessions(sessions=[self.slims_sessions], subject_id="000000")
        self.assertEqual(len(sessions), 1)
        mapped_session_json = sessions[0].model_dump_json()
        mapped_session_json_parsed = json.loads(mapped_session_json)
        self.assertEqual(mapped_session_json_parsed, self.expected_session)


if __name__ == "__main__":
    unittest.main()
