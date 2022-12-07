"""Module to test LabTracksResponseHandler methods."""
import unittest

from aind_metadata_service.labtracks.client import (
    ErrorResponseHandler,
    LabTracksResponseHandler
)


class TestLabTracksErrorResponseHandler(unittest.TestCase):
    """Class for unit tests on LabTracksErrorResponseHandler."""
    test_response = 'null'
    rh = LabTracksResponseHandler()
    def test_id_does_not_exist(self):
        expected_response = {
            "msg": f"{ErrorResponseHandler.ErrorResponses.ID_ERROR.value}: " f"InternalError"
        }
        actual_response = self.rh.map_response_to_subject(self.test_response)
        self.assertEqual(expected_response,actual_response)
        

if __name__ == "__main__":
    unittest.main()
