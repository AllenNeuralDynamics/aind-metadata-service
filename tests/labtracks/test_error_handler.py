"""Module to test LabTracksResponseHandler methods."""
import unittest
from unittest.mock import Mock, patch
from fastapi.responses import JSONResponse

from aind_metadata_service.labtracks.client import (
    ErrorResponseHandler,
    LabTracksClient
)

class TestLabTracksErrorResponseHandler(unittest.TestCase):
    """Class for unit tests on LabTracksErrorResponseHandler."""
    driver = "{FreeTDS}"
    server = "0.0.0.0"
    port = "1234"
    db = "LabTracksDB"
    user = "LabTracksUser"
    password = "LabTracksPassword"
    lb_client = LabTracksClient(
        driver=driver,
        server=server,
        port=port,
        db=db,
        user=user,
        password=password,
    )

    test_response = {"msg":[]}
    subject_id = '0000'

    @patch("pyodbc.connect")
    def test_id_does_not_exist(self, mock_connect: Mock):

        expected_response = JSONResponse(status_code=418, 
                content={"message": f"{ErrorResponseHandler.ErrorResponses.ID_ERROR.value}: "
                f"subject {self.subject_id} does not exist", "data": self.test_response})

        actual_response = self.lb_client.get_subject_from_subject_id(self.subject_id)
        self.assertEqual(expected_response.body,actual_response.body)
        

if __name__ == "__main__":
    unittest.main()
