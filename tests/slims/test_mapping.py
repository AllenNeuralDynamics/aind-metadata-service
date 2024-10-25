import unittest
from pathlib import Path
import os
import json
from aind_slims_api.operations.ecephys_session import EcephysSession as SlimsEcephysSession
from aind_metadata_service.slims.mapping import SlimsSessionMapper

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "resources" / "slims"
RAW_DIR = RESOURCES_DIR / "raw"
MAPPED_DIR = RESOURCES_DIR / "mapped"

class TestSlimsSessionMapper(unittest.TestCase):
    """Class to test methods of SLimsSessionMapper"""

    def setUp(self):
        """Sets up test class"""
        self.mapper = SlimsSessionMapper()
        with open(f"{RAW_DIR}/ecephys_session_json_entity.json", "r") as f:
            slims_data1 = json.load(f)
        with open(f"{RAW_DIR}/ecephys_session_json_entity2.json", "r") as f:
            slims_data2 = json.load(f)
        with open(f"{MAPPED_DIR}/ecephys_session.json", encoding="utf-8") as f:
            expected_data1 = json.load(f)
        with open(f"{MAPPED_DIR}/ecephys_session2.json", encoding="utf-8") as f:
            expected_data2 = json.load(f)
        self.slims_sessions = [
            SlimsEcephysSession.model_validate(slims_data1),
            SlimsEcephysSession.model_validate(slims_data2)
        ]
        self.expected_sessions = [expected_data1, expected_data2]

    def test_map_sessions(self):
        """Tests map sessions"""
        sessions = self.mapper.map_sessions(sessions=self.slims_sessions, subject_id="000000")
        self.assertEqual(len(sessions), 2)
        mapped_session_json1 = sessions[0].model_dump_json()
        mapped_session_json_parsed1 = json.loads(mapped_session_json1)
        self.assertEqual(mapped_session_json_parsed1, self.expected_sessions[0])
        mapped_session_json2 = sessions[1].model_dump_json()
        mapped_session_json_parsed2 = json.loads(mapped_session_json2)
        self.assertEqual(mapped_session_json_parsed2, self.expected_sessions[1])


if __name__ == "__main__":
    unittest.main()
