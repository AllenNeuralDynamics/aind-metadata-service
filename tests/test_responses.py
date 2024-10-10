"""Tests responses module"""

import unittest

from aind_metadata_service.responses import (
    InternalServerError,
    InvalidModelResponse,
    Message,
    NoDataFound,
)


class TestResponses(unittest.TestCase):
    """Test response models construction"""

    def test_message(self):
        """Test Message model"""

        response = Message(message="hello world", data=[{"key1": "val1"}])
        response_json = response.model_dump_json()
        deser_response = Message.model_validate_json(response_json)
        self.assertEqual(response, deser_response)

    def test_invalid_model_response(self):
        """Test Invalid model"""

        response = InvalidModelResponse(
            message="hello world", data={"key1": "val1"}
        )
        response_json = response.model_dump_json()
        deser_response = InvalidModelResponse.model_validate_json(
            response_json
        )
        self.assertEqual(response, deser_response)

    def test_internal_server_error(self):
        """Test InternalServerError"""

        response = InternalServerError()
        self.assertEqual("Internal Server Error", response.message)
        self.assertIsNone(response.data)

    def test_no_data_found(self):
        """Test NoDataFound"""

        response = NoDataFound()
        self.assertEqual("No Data Found", response.message)
        self.assertIsNone(response.data)


if __name__ == "__main__":
    unittest.main()
