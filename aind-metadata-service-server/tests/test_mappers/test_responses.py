"""Tests mapping pydantic models to JSONResponses."""

import json
import unittest
from unittest.mock import patch, MagicMock

from pydantic import BaseModel, ValidationError

from aind_metadata_service_server.mappers.responses import map_to_response


class ExampleModel(BaseModel):
    """Model for testing purposes."""

    name: str
    id: int
    val: str = "default_value"


class TestResponses(unittest.TestCase):
    """Test methods in responses module"""

    def test_map_to_200_response(self):
        """Tests valid model is mapped to a 200 response."""

        model = ExampleModel(name="abc", id=123)
        response = map_to_response(model=model)
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {"name": "abc", "id": 123, "val": "default_value"},
            json.loads(response.body.decode("utf-8")),
        )

    def test_map_to_400_response(self):
        """Tests invalid model is mapped to a 400 response."""

        model = ExampleModel.model_construct(name="abc")
        with self.assertLogs(level="DEBUG") as captured:
            response = map_to_response(model=model)
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            {"name": "abc", "val": "default_value"},
            json.loads(response.body.decode("utf-8")),
        )
        expected_error_message = "Field required"
        response_header_msg = json.loads(response.headers["x-error-message"])[
            0
        ]["msg"]
        self.assertEqual(expected_error_message, response_header_msg)
        self.assertEqual(1, len(captured.output))

    def test_map_multiple_to_200_response(self):
        """Tests valid list of models is mapped to a 200 response."""

        models = [
            ExampleModel(name="abc", id=123),
            ExampleModel(name="def", id=456, val="custom_value"),
            ExampleModel(name="ghi", id=789),
        ]
        response = map_to_response(model=models)
        self.assertEqual(200, response.status_code)

        expected_content = [
            {"name": "abc", "id": 123, "val": "default_value"},
            {"name": "def", "id": 456, "val": "custom_value"},
            {"name": "ghi", "id": 789, "val": "default_value"},
        ]
        self.assertEqual(
            expected_content,
            json.loads(response.body.decode("utf-8")),
        )

    def test_map_multiple_to_400_response(self):
        """Tests invalid list of models is mapped to a 400 response."""

        models = [
            ExampleModel.model_construct(name=None, id=123),
            ExampleModel.model_construct(name="def", id=None, val=None),
            ExampleModel.model_construct(name="ghi", id=None),
        ]
        response = map_to_response(model=models)
        self.assertEqual(400, response.status_code)

        expected_content = [
            {"name": None, "id": 123, "val": "default_value"},
            {"name": "def", "id": None, "val": None},
            {"name": "ghi", "id": None, "val": "default_value"},
        ]
        self.assertEqual(
            expected_content,
            json.loads(response.body.decode("utf-8")),
        )

    def test_map_to_400_response_with_long_error_message(self):
        """Tests that long error message raises expected message."""

        long_error_message = "x" * 4000
        model = ExampleModel.model_construct(name="abc")

        with patch.object(ExampleModel, "model_validate") as mock_validate:
            mock_error = ValidationError.from_exception_data(
                "ExampleModel", []
            )
            mock_error.json = MagicMock(return_value=long_error_message)
            mock_validate.side_effect = mock_error

            response = map_to_response(model=model)

        self.assertEqual(400, response.status_code)
        self.assertEqual(
            "Too many validation errors. Please validate locally.",
            response.headers["x-error-message"],
        )


if __name__ == "__main__":
    unittest.main()
