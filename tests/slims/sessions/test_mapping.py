"""Tests Slims Mapper"""

import json
import os
import unittest
from pathlib import Path

from aind_data_schema.components.devices import SpoutSide
from aind_data_schema.core.session import RewardSolution
from aind_slims_api.models.ecephys_session import SlimsRewardDeliveryRdrc
from aind_slims_api.operations.ecephys_session import (
    EcephysSession as SlimsEcephysSession,
)

from aind_metadata_service.slims.sessions.mapping import SlimsSessionMapper

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
)
RAW_DIR = RESOURCES_DIR / "raw"
MAPPED_DIR = RESOURCES_DIR / "mapped"


class TestSlimsSessionMapper(unittest.TestCase):
    """Class to test methods of SLimsSessionMapper"""

    def setUp(self):
        """Sets up test class"""
        self.mapper = SlimsSessionMapper()
        with open(RAW_DIR / "ecephys_session_response.json") as f:
            slims_data1 = json.load(f)
        with open(RAW_DIR / "ecephys_session_response2.json") as f:
            slims_data2 = json.load(f)
        with open(MAPPED_DIR / "ecephys_session.json") as f:
            expected_data1 = json.load(f)
        with open(MAPPED_DIR / "ecephys_session2.json") as f:
            expected_data2 = json.load(f)
        self.slims_sessions = [
            SlimsEcephysSession.model_validate(slims_data1),
            SlimsEcephysSession.model_validate(slims_data2),
        ]
        self.expected_sessions = [expected_data1, expected_data2]

    def test_map_sessions(self):
        """Tests map sessions"""
        sessions = self.mapper.map_sessions(
            sessions=self.slims_sessions, subject_id="000000"
        )
        self.assertEqual(len(sessions), 2)
        mapped_session_json1 = sessions[0].model_dump_json()
        mapped_session_json_parsed1 = json.loads(mapped_session_json1)
        self.assertEqual(
            mapped_session_json_parsed1, self.expected_sessions[0]
        )
        mapped_session_json2 = sessions[1].model_dump_json()
        mapped_session_json_parsed2 = json.loads(mapped_session_json2)
        self.assertEqual(
            mapped_session_json_parsed2, self.expected_sessions[1]
        )

    def test_map_spout_side(self):
        """Tests spout side is mapped correctly."""
        self.assertEqual(self.mapper._map_spout_side("left"), SpoutSide.LEFT)
        self.assertEqual(self.mapper._map_spout_side("LEFT"), SpoutSide.LEFT)
        self.assertEqual(
            self.mapper._map_spout_side("Left side"), SpoutSide.LEFT
        )
        self.assertEqual(self.mapper._map_spout_side("right"), SpoutSide.RIGHT)
        self.assertEqual(self.mapper._map_spout_side("RIGHT"), SpoutSide.RIGHT)
        self.assertEqual(
            self.mapper._map_spout_side("Right spout"), SpoutSide.RIGHT
        )
        self.assertEqual(
            self.mapper._map_spout_side("center"), SpoutSide.CENTER
        )
        self.assertEqual(
            self.mapper._map_spout_side("CENTER"), SpoutSide.CENTER
        )
        self.assertEqual(
            self.mapper._map_spout_side("Center spout"), SpoutSide.CENTER
        )
        self.assertEqual(
            self.mapper._map_spout_side("unknown"), SpoutSide.OTHER
        )
        self.assertEqual(
            self.mapper._map_spout_side("random text"), SpoutSide.OTHER
        )
        self.assertEqual(self.mapper._map_spout_side(""), SpoutSide.OTHER)

    def test_map_reward_solution(self):
        """Tests that reward solution is mapper correctly."""
        reward_delivery = SlimsRewardDeliveryRdrc.model_construct(
            reward_solution="Other, (if Other, specify below)",
            other_reward_solution="Some Solution",
        )
        solution, notes = self.mapper._map_reward_solution(reward_delivery)
        self.assertEqual(solution, RewardSolution.OTHER)
        self.assertEqual(notes, "Some Solution")

        reward_delivery2 = SlimsRewardDeliveryRdrc.model_construct(
            reward_solution=None, other_reward_solution=None
        )
        self.assertEqual(
            (None, None), self.mapper._map_reward_solution(reward_delivery2)
        )


if __name__ == "__main__":
    unittest.main()
