"""Module to test SharePoint Client methods"""

import json
import logging
import os
import unittest
from pathlib import Path
from typing import List, Tuple
from unittest.mock import MagicMock, Mock, patch

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.sharepoint.client import (
    SharePointClient,
    SharepointSettings,
)
from pydantic import SecretStr
from tests import PYD_VERSION

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
DIR_RAW_2019 = TEST_DIR / "resources" / "sharepoint" / "nsb2019" / "raw"
DIR_MAP_2019 = TEST_DIR / "resources" / "sharepoint" / "nsb2019" / "mapped"
LIST_ITEM_FILE_NAMES_2019 = os.listdir(DIR_RAW_2019)
sorted(LIST_ITEM_FILE_NAMES_2019)
LIST_ITEM_FILE_PATHS_2019 = [
    DIR_RAW_2019 / str(f) for f in LIST_ITEM_FILE_NAMES_2019
]
MAPPED_ITEM_FILE_NAMES_2019 = os.listdir(DIR_MAP_2019)
sorted(MAPPED_ITEM_FILE_NAMES_2019)
MAPPED_FILE_PATHS_2019 = [
    DIR_MAP_2019 / str(f) for f in MAPPED_ITEM_FILE_NAMES_2019
]
DIR_RAW_2023 = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "raw"
DIR_MAP_2023 = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "mapped"
LIST_ITEM_FILE_NAMES_2023 = os.listdir(DIR_RAW_2023)
sorted(LIST_ITEM_FILE_NAMES_2023)
LIST_ITEM_FILE_PATHS_2023 = [
    DIR_RAW_2023 / str(f) for f in LIST_ITEM_FILE_NAMES_2023
]
MAPPED_ITEM_FILE_NAMES_2023 = os.listdir(DIR_MAP_2023)
sorted(MAPPED_ITEM_FILE_NAMES_2023)
MAPPED_FILE_PATHS_2023 = [
    DIR_MAP_2023 / str(f) for f in MAPPED_ITEM_FILE_NAMES_2023
]

DIR_RAW_2020 = TEST_DIR / "resources" / "sharepoint" / "las2020" / "raw"
DIR_MAP_2020 = TEST_DIR / "resources" / "sharepoint" / "las2020" / "mapped"
LIST_ITEM_FILE_NAMES_2020 = os.listdir(DIR_RAW_2020)
sorted(LIST_ITEM_FILE_NAMES_2020)
LIST_ITEM_FILE_PATHS_2020 = [
    DIR_RAW_2020 / str(f) for f in LIST_ITEM_FILE_NAMES_2020
]
MAPPED_ITEM_FILE_NAMES_2020 = os.listdir(DIR_MAP_2020)
sorted(MAPPED_ITEM_FILE_NAMES_2020)
MAPPED_FILE_PATHS_2020 = [
    DIR_MAP_2020 / str(f) for f in MAPPED_ITEM_FILE_NAMES_2020
]

INJECTION_MATERIALS_PATH = (
    TEST_DIR / "resources" / "tars" / "mapped_materials.json"
)


class TestSharepointSettings(unittest.TestCase):
    """Class to test methods for SharepointSettings."""

    EXAMPLE_ENV_VAR = {
        "SHAREPOINT_AIND_SITE_ID": "aind_site_123",
        "SHAREPOINT_LAS_SITE_ID": "las_site_456",
        "SHAREPOINT_NSB_2019_LIST_ID": "nsb_2019",
        "SHAREPOINT_NSB_2023_LIST_ID": "nsb_2023",
        "SHAREPOINT_LAS_2020_LIST_ID": "las_2020",
        "SHAREPOINT_CLIENT_ID": "client_id",
        "SHAREPOINT_CLIENT_SECRET": "client_secret",
        "SHAREPOINT_TENANT_ID": "tenant_id",
    }

    @patch.dict(os.environ, EXAMPLE_ENV_VAR, clear=True)
    def test_settings_set_from_env_vars(self):
        """Tests that the settings can be set from env vars."""
        settings1 = SharepointSettings()
        settings2 = SharepointSettings(aind_site_id="other_site")
        self.assertEqual("aind_site_123", settings1.aind_site_id)
        self.assertEqual("las_site_456", settings1.las_site_id)
        self.assertEqual("nsb_2019", settings1.nsb_2019_list_id)
        self.assertEqual("nsb_2023", settings1.nsb_2023_list_id)
        self.assertEqual("las_2020", settings1.las_2020_list_id)
        self.assertEqual("client_id", settings1.client_id)
        self.assertEqual("client_secret", settings1.client_secret.get_secret_value())
        self.assertEqual("tenant_id", settings1.tenant_id)
        self.assertEqual("other_site", settings2.aind_site_id)
        self.assertEqual("las_site_456", settings2.las_site_id)

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_errors(self):
        """Tests that errors are raised if settings are incorrect."""

        with self.assertRaises(ValueError) as e:
            SharepointSettings(aind_site_id="aind_site_only")

        expected_error_message = (
            "7 validation errors for SharepointSettings\n"
            "las_site_id\n"
            "  Field required [type=missing, input_value={'aind_site_id': "
            "'aind_site_only'}, input_type=dict]\n"
            "    For further information visit "
            f"https://errors.pydantic.dev/{PYD_VERSION}/v/missing\n"
            "nsb_2019_list_id\n"
            "  Field required [type=missing, input_value={'aind_site_id': "
            "'aind_site_only'}, input_type=dict]\n"
            "    For further information visit "
            f"https://errors.pydantic.dev/{PYD_VERSION}/v/missing\n"
            "nsb_2023_list_id\n"
            "  Field required [type=missing, input_value={'aind_site_id': "
            "'aind_site_only'}, input_type=dict]\n"
            "    For further information visit "
            f"https://errors.pydantic.dev/{PYD_VERSION}/v/missing\n"
            "las_2020_list_id\n"
            "  Field required [type=missing, input_value={'aind_site_id': "
            "'aind_site_only'}, input_type=dict]\n"
            "    For further information visit "
            f"https://errors.pydantic.dev/{PYD_VERSION}/v/missing\n"
            "client_id\n"
            "  Field required [type=missing, input_value={'aind_site_id': "
            "'aind_site_only'}, input_type=dict]\n"
            "    For further information visit "
            f"https://errors.pydantic.dev/{PYD_VERSION}/v/missing\n"
            "client_secret\n"
            "  Field required [type=missing, input_value={'aind_site_id': "
            "'aind_site_only'}, input_type=dict]\n"
            "    For further information visit "
            f"https://errors.pydantic.dev/{PYD_VERSION}/v/missing\n"
            "tenant_id\n"
            "  Field required [type=missing, input_value={'aind_site_id': "
            "'aind_site_only'}, input_type=dict]\n"
            "    For further information visit "
            f"https://errors.pydantic.dev/{PYD_VERSION}/v/missing"
        )

        self.assertEqual(expected_error_message, repr(e.exception))


class TestSharepointClient(unittest.TestCase):
    """Class to test methods for SharePointClient."""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        cls.list_items_2019 = cls._load_json_files(year="2019")
        cls.list_items_2023 = cls._load_json_files(year="2023")
        cls.list_items_2020 = cls._load_json_files(year="2020")

        cls.client = SharePointClient(
            aind_site_id="aind_site_123",
            las_site_id="las_site_456",
            nsb_2019_list_id="nsb_2019",
            nsb_2023_list_id="nsb_2023",
            las_2020_list_id="las_2020",
            client_id="client_id",
            client_secret=SecretStr("client_secret"),
            tenant_id="tenant_id",
        )
        # Patch get_access_token so that header construction works without real HTTP calls.
        cls.client.get_access_token = MagicMock(return_value="fake-token")

    @staticmethod
    def _load_json_files(year: str) -> List[Tuple[dict, dict, str]]:
        """Reads raw data and expected data into json"""
        list_items = []
        if year == "2019":
            list_item_file_paths = LIST_ITEM_FILE_PATHS_2019
        elif year == "2023":
            list_item_file_paths = LIST_ITEM_FILE_PATHS_2023
        else:
            list_item_file_paths = LIST_ITEM_FILE_PATHS_2020
        for file_path in list_item_file_paths:
            mapped_file_path = (
                file_path.parent.parent
                / "mapped"
                / ("mapped_" + file_path.name)
            )
            with open(file_path) as f:
                contents = json.load(f)
            with open(mapped_file_path, encoding="utf-8") as f:
                mapped_contents = json.load(f)
            list_items.append((contents, mapped_contents, file_path.name))
            list_items.sort(key=lambda x: x[2])
        return list_items

    def test_empty_response(self):
        """Tests that an empty response is generated if no data returned
        from NSB datatbases"""
        with patch.object(self.client, "_fetch_list_items", return_value={"value": []}):
            response = self.client.get_procedure_info(subject_id="12345", list_id="nsb_2019")

        self.assertEqual(StatusCodes.DB_RESPONDED, response.status_code)
        self.assertEqual([], response.aind_models)
        json_response = response.map_to_json_response()
        self.assertEqual(StatusCodes.NO_DATA_FOUND.value, json_response.status_code)

    def test_data_mapped(self):
        """Tests that 200 response returned correctly."""
        list_item_2019_raw = self.list_items_2019[0][0]
        list_item_2023_raw = self.list_items_2023[0][0]
        expected_mapped_2019 = self.list_items_2019[0][1]
        expected_mapped_2023 = self.list_items_2023[0][1]

        # Patch _fetch_list_items to simulate the Graph API response.
        with patch.object(
            self.client,
            "_fetch_list_items",
            side_effect=[
                {"value": [{"fields": list_item_2019_raw}]},
                {"value": [{"fields": list_item_2023_raw}]},
            ],
        ):
            with patch.object(
                self.client,
                "_extract_procedures_from_response",
                side_effect=[expected_mapped_2019, expected_mapped_2023],
            ):
                response2019 = self.client.get_procedure_info(
                    subject_id="12345", list_id="nsb_2019"
                )
                response2023 = self.client.get_procedure_info(
                    subject_id="12345", list_id="nsb_2023"
                )

        merged_response = self.client.merge_responses([response2019, response2023])
        json_response = merged_response.map_to_json_response()
        actual_content = json.loads(json_response.body.decode("utf-8"))
        actual_subject_procedures = actual_content["data"]["subject_procedures"]
        expected_subject_procedures = expected_mapped_2019 + expected_mapped_2023
        expected_subject_procedures.sort(key=lambda x: str(x))
        actual_subject_procedures.sort(key=lambda x: str(x))
        self.assertEqual(StatusCodes.DB_RESPONDED, merged_response.status_code)
        self.assertEqual(406, json_response.status_code)
        self.assertEqual(expected_subject_procedures, actual_subject_procedures)

    def test_las_data_mapped(self):
        """Tests that 200 response returned correctly."""
        list_item_2020_raw = self.list_items_2020[0][0]
        expected_mapped_2020 = self.list_items_2020[0][1]

        # Patch _fetch_list_items to simulate the Graph API response for LAS.
        with patch.object(
            self.client,
            "_fetch_list_items",
            return_value={"value": [{"fields": list_item_2020_raw}]}
        ):
            with patch.object(
                self.client,
                "_extract_procedures_from_response",
                return_value=expected_mapped_2020
            ):
                response = self.client.get_procedure_info(subject_id="000000", list_id="las_2020")
        self.assertEqual(StatusCodes.DB_RESPONDED, response.status_code)
        json_response = response.map_to_json_response()
        actual_content = json.loads(json_response.body.decode("utf-8"))
        actual_subject_procedures = actual_content["data"]["subject_procedures"]
        self.assertEqual(expected_mapped_2020, actual_subject_procedures)
        self.assertEqual(406, json_response.status_code)

    @patch("aind_metadata_service.sharepoint.client.ClientContext")
    def test_merge_valid_empty_procedures(
        self, mock_sharepoint_client: MagicMock
    ):
        """Tests that merging valid procedures list with empty list
        returned correctly."""

        inner_mock = MagicMock()
        mock_sharepoint_client.return_value.with_credentials.return_value = (
            inner_mock
        )
        mock_list_views = MagicMock()
        inner_mock.web.lists.get_by_title.return_value.views = mock_list_views
        mock_list_items = MagicMock()
        mock_list_views.get_by_title.return_value.get_items.return_value = (
            mock_list_items
        )
        list_item_2019_1 = self.list_items_2019[0][0]
        list_item_2023_1 = self.list_items_2023[0][0]
        mock_list_item2019 = MagicMock()
        mock_list_item2023 = MagicMock()
        mock_list_item2019.to_json.return_value = list_item_2019_1
        mock_list_item2023.to_json.return_value = list_item_2023_1
        mock_list_items.filter.side_effect = [
            [mock_list_item2019],
            [mock_list_item2023],
        ]

        client = SharePointClient(
            nsb_site_url="some_url",
            las_site_url="some_other_url",
            client_id="some_client_id",
            client_secret="some_client_secret",
            nsb_2019_list_title="some_list_title2019",
            nsb_2023_list_title="some_list_title2023",
            las_2020_list_title="some_list_title2020",
        )

        response2019 = client.get_procedure_info(
            subject_id="12345", list_title="some_list_title2019"
        )
        response2019_empty = ModelResponse(
            aind_models=[], status_code=StatusCodes.DB_RESPONDED
        )

        expected_subject_procedures_left = self.list_items_2019[0][1]

        expected_subject_procedures_right = self.list_items_2019[0][1]
        merged_responses_left = client.merge_responses(
            [response2019, response2019_empty]
        )
        json_response_left = merged_responses_left.map_to_json_response()
        actual_content_left = json.loads(
            json_response_left.body.decode("utf-8")
        )
        actual_subject_procedures_left = actual_content_left["data"][
            "subject_procedures"
        ]

        merged_responses_right = client.merge_responses(
            [response2019_empty, response2019]
        )
        json_response_right = merged_responses_right.map_to_json_response()
        actual_content_right = json.loads(
            json_response_right.body.decode("utf-8")
        )
        actual_subject_procedures_right = actual_content_right["data"][
            "subject_procedures"
        ]
        expected_subject_procedures_left.sort(key=lambda x: str(x))
        actual_subject_procedures_left.sort(key=lambda x: str(x))

        expected_subject_procedures_right.sort(key=lambda x: str(x))
        actual_subject_procedures_right.sort(key=lambda x: str(x))
        self.assertEqual(
            StatusCodes.DB_RESPONDED, merged_responses_left.status_code
        )
        # Most of the models are missing required fields not stored by NSB
        self.assertEqual(406, json_response_left.status_code)
        self.assertEqual(
            expected_subject_procedures_left, actual_subject_procedures_left
        )
        self.assertEqual(
            StatusCodes.DB_RESPONDED, merged_responses_right.status_code
        )
        # Most of the models are missing required fields not stored by NSB
        self.assertEqual(406, json_response_right.status_code)
        self.assertEqual(
            expected_subject_procedures_right, actual_subject_procedures_right
        )

    @patch("aind_metadata_service.sharepoint.client.ClientContext")
    @patch(
        "aind_metadata_service.sharepoint.nsb2023.procedures."
        "NSB2023Procedures.get_procedures_from_sharepoint"
    )
    @patch("logging.error")
    def test_merge_valid_error_procedures(
        self,
        mock_log: MagicMock,
        mock_error: MagicMock,
        mock_sharepoint_client: MagicMock,
    ):
        """Tests that merging valid and error responses returned correctly."""

        inner_mock = MagicMock()
        mock_sharepoint_client.return_value.with_credentials.return_value = (
            inner_mock
        )
        mock_list_views = MagicMock()
        inner_mock.web.lists.get_by_title.return_value.views = mock_list_views
        mock_list_items = MagicMock()
        mock_list_views.get_by_title.return_value.get_items.return_value = (
            mock_list_items
        )
        list_item_2019_1 = self.list_items_2019[0][0]
        list_item_2023_1 = self.list_items_2023[0][0]
        mock_list_item2019 = MagicMock()
        mock_list_item2023 = MagicMock()
        mock_list_item2019.to_json.return_value = list_item_2019_1
        mock_list_item2023.to_json.return_value = list_item_2023_1
        mock_list_items.filter.side_effect = [
            [mock_list_item2019],
            [mock_list_item2023],
        ]

        client = SharePointClient(
            nsb_site_url="some_url",
            las_site_url="some_other_url",
            client_id="some_client_id",
            client_secret="some_client_secret",
            nsb_2019_list_title="some_list_title2019",
            nsb_2023_list_title="some_list_title2023",
            las_2020_list_title="some_list_title2020",
        )

        response2019 = client.get_procedure_info(
            subject_id="12345", list_title="some_list_title2019"
        )
        mock_error.side_effect = Mock(side_effect=BrokenPipeError)
        response2023_error = client.get_procedure_info(
            subject_id="12345", list_title="some_list_title2023"
        )

        expected_subject_procedures = self.list_items_2019[0][1]

        merged_responses = client.merge_responses(
            [response2023_error, response2019]
        )
        json_response = merged_responses.map_to_json_response()
        actual_content = json.loads(json_response.body.decode("utf-8"))
        actual_subject_procedures = actual_content["data"][
            "subject_procedures"
        ]
        expected_subject_procedures.sort(key=lambda x: str(x))
        actual_subject_procedures.sort(key=lambda x: str(x))

        self.assertEqual(
            StatusCodes.MULTI_STATUS, merged_responses.status_code
        )
        self.assertEqual(207, json_response.status_code)
        self.assertEqual(
            expected_subject_procedures, actual_subject_procedures
        )
        mock_log.assert_called_once_with("BrokenPipeError()")

    @patch("aind_metadata_service.sharepoint.client.ClientContext")
    def test_merge_three_responses(self, mock_sharepoint_client: MagicMock):
        """Tests that multi status is returned as expected."""
        inner_mock = MagicMock()
        mock_sharepoint_client.return_value.with_credentials.return_value = (
            inner_mock
        )
        mock_list_views = MagicMock()
        inner_mock.web.lists.get_by_title.return_value.views = mock_list_views
        mock_list_items = MagicMock()
        mock_list_views.get_by_title.return_value.get_items.return_value = (
            mock_list_items
        )
        list_item_2019_1 = self.list_items_2019[0][0]
        mock_list_item2019 = MagicMock()
        mock_list_item2019.to_json.return_value = list_item_2019_1
        mock_list_items.filter.side_effect = [
            [mock_list_item2019],
        ]
        client = SharePointClient(
            nsb_site_url="some_url",
            las_site_url="some_other_url",
            client_id="some_client_id",
            client_secret="some_client_secret",
            nsb_2019_list_title="some_list_title2019",
            nsb_2023_list_title="some_list_title2023",
            las_2020_list_title="some_list_title2020",
        )

        response1 = ModelResponse.internal_server_error_response()
        response2 = ModelResponse.internal_server_error_response()
        response3 = client.get_procedure_info(
            subject_id="12345", list_title="some_list_title2019"
        )
        merged_responses = client.merge_responses(
            [response1, response2, response3]
        )
        actual_json = merged_responses.map_to_json_response()
        expected_content = jsonable_encoder(
            json.loads(response3.aind_models[0].model_dump_json())
        )
        expected_json = JSONResponse(
            status_code=207,
            content=(
                {
                    "message": (
                        "There was an error retrieving records from one or "
                        "more of the databases."
                    ),
                    "data": expected_content,
                }
            ),
        )

        self.assertEqual(
            StatusCodes.MULTI_STATUS, merged_responses.status_code
        )
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_merge_procedures_empty_input(self):
        """Tests that merging nothing returns internal server error."""

        client = SharePointClient(
            nsb_site_url="some_url",
            las_site_url="some_other_url",
            client_id="some_client_id",
            client_secret="some_client_secret",
            nsb_2019_list_title="some_list_title2019",
            nsb_2023_list_title="some_list_title2023",
            las_2020_list_title="some_list_title2020",
        )

        merged_responses = client.merge_responses([])
        actual_json = merged_responses.map_to_json_response()
        expected_json = JSONResponse(
            status_code=500,
            content=(
                {
                    "message": "Internal Server Error.",
                    "data": None,
                }
            ),
        )

        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR, merged_responses.status_code
        )
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_merge_error_responses(self):
        """Tests that merging error responses returns internal server error."""

        client = SharePointClient(
            nsb_site_url="some_url",
            las_site_url="some_other_url",
            client_id="some_client_id",
            client_secret="some_client_secret",
            nsb_2019_list_title="some_list_title2019",
            nsb_2023_list_title="some_list_title2023",
            las_2020_list_title="some_list_title2020",
        )

        response1 = ModelResponse.internal_server_error_response()
        response2 = ModelResponse.connection_error_response()
        merged_responses = client.merge_responses([response1, response2])
        actual_json = merged_responses.map_to_json_response()
        expected_json = JSONResponse(
            status_code=500,
            content=(
                {
                    "message": "Internal Server Error.",
                    "data": None,
                }
            ),
        )

        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR, merged_responses.status_code
        )
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    @patch(
        "aind_metadata_service.sharepoint.nsb2023.procedures."
        "NSB2023Procedures.get_procedures_from_sharepoint"
    )
    @patch("logging.error")
    def test_error_response(
        self,
        mock_log: MagicMock,
        mock_error: MagicMock,
    ):
        """Tests internal server error response caught correctly."""

        client = SharePointClient(
            nsb_site_url="some_url",
            las_site_url="some_other_url",
            client_id="some_client_id",
            client_secret="some_client_secret",
            nsb_2019_list_title="some_list_title2019",
            nsb_2023_list_title="some_list_title2023",
            las_2020_list_title="some_list_title2020",
        )

        mock_error.side_effect = Mock(side_effect=BrokenPipeError)

        model_response = client.get_procedure_info(
            subject_id="12345", list_title="some_list_title2023"
        )
        json_response = model_response.map_to_json_response()
        mock_log.assert_called_once_with("BrokenPipeError()")
        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR, model_response.status_code
        )
        self.assertEqual([], model_response.aind_models)
        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR.value, json_response.status_code
        )
        self.assertIsNone(
            json.loads(json_response.body.decode("utf-8"))["data"]
        )

    @patch("logging.error")
    def test_corrupt_list_title(self, mock_log: MagicMock):
        """Tests that an error is logged if a corrupt list title is input."""

        client = SharePointClient(
            nsb_site_url="some_url",
            las_site_url="some_other_url",
            client_id="some_client_id",
            client_secret="some_client_secret",
            nsb_2019_list_title="some_list_title2019",
            nsb_2023_list_title="some_list_title2023",
            las_2020_list_title="some_list_title2020",
        )

        model_response = client.get_procedure_info(
            subject_id="12345", list_title="some_list_title"
        )

        mock_log.assert_called_once_with(
            "Exception('Unknown NSB Sharepoint List: some_list_title')"
        )

        self.assertEqual(
            ModelResponse.internal_server_error_response().status_code,
            model_response.status_code,
        )
        self.assertEqual([], model_response.aind_models)


if __name__ == "__main__":
    unittest.main()
