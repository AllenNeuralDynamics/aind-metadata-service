import unittest
from pathlib import Path
import os
import json
from unittest.mock import MagicMock, patch
from aind_data_schema.core.session import Session, Stream, StimulusEpoch, RewardDeliveryConfig
from aind_slims_api.operations.ecephys_session import EcephysSession, SlimsRewardDeliveryInfo
from aind_slims_api.models.ecephys_session import SlimsRewardDeliveryRdrc
from aind_metadata_service.slims.mapping import SlimsSessionMapper, SlimsStream, SlimsRewardSpoutsRdrc, SlimsStimulusEpochsResult

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
        with open(EXPECTED_SESSIONS, "r") as file:
            expected = json.load(file)
        self.slims_sessions = EcephysSession.model_validate(slims_data)
        self.expected_sessions = Session.model_construct(expected)

    def test_map_sessions(self):
        sessions = self.mapper.map_sessions(sessions=[self.slims_sessions], subject_id="000000")
        self.assertEqual(sessions, [self.expected_sessions])


if __name__ == "__main__":
    unittest.main()
