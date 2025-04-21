"""Module to test SharePoint Client methods"""

import json
import logging
import os
import unittest
from pathlib import Path
from typing import List, Tuple
from unittest.mock import MagicMock, call, patch

import requests
from fastapi.responses import JSONResponse
from pydantic import SecretStr

from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.sharepoint.client import (
    SharePointClient,
    SharepointSettings,
)
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
INTENDED_MEASUREMENTS_PATH = (
    TEST_DIR
    / "resources"
    / "sharepoint"
    / "nsb2023"
    / "nsb2023_intended_measurements.json"
)


class TestSharepointSettings(unittest.TestCase):
    """Class to test methods for SharepointSettings."""

    EXAMPLE_ENV_VAR = {
        "SHAREPOINT_AIND_SITE_ID": "aind_site_123",
        "SHAREPOINT_LAS_SITE_ID": "las_site_456",
        "SHAREPOINT_NSB_2019_LIST_ID": "nsb_2019",
        "SHAREPOINT_NSB_2023_LIST_ID": "nsb_2023",
        "SHAREPOINT_NSB_PRESENT_LIST_ID": "nsb_present",
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
        self.assertEqual("nsb_present", settings1.nsb_present_list_id)
        self.assertEqual("las_2020", settings1.las_2020_list_id)
        self.assertEqual("client_id", settings1.client_id)
        self.assertEqual(
            "client_secret", settings1.client_secret.get_secret_value()
        )
        self.assertEqual("tenant_id", settings1.tenant_id)
        self.assertEqual("other_site", settings2.aind_site_id)
        self.assertEqual("las_site_456", settings2.las_site_id)
        self.assertEqual(
            "https://graph.microsoft.com/v1.0", settings1.graph_api_url
        )
        self.assertEqual(
            "https://graph.microsoft.com/.default", settings1.scope
        )
        self.assertEqual(
            "https://login.microsoftonline.com/tenant_id/oauth2/v2.0/token",
            settings1.token_url,
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_errors(self):
        """Tests that errors are raised if settings are incorrect."""

        with self.assertRaises(ValueError) as e:
            SharepointSettings(aind_site_id="aind_site_only")

        expected_error_message = (
            "9 validation errors for SharepointSettings\n"
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
            "nsb_present_list_id\n"
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
            f"https://errors.pydantic.dev/{PYD_VERSION}/v/missing\n"
            "token_url\n"
            "  Value error, tenant_id must be provided to generate token_url "
            "[type=value_error, input_value=None, input_type=NoneType]\n"
            "    For further information visit "
            f"https://errors.pydantic.dev/{PYD_VERSION}/v/value_error"
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
        cls.settings = SharepointSettings(
            aind_site_id="aind_site_123",
            las_site_id="las_site_456",
            nsb_2019_list_id="nsb_2019",
            nsb_2023_list_id="nsb_2023",
            nsb_present_list_id="nsb_present",
            las_2020_list_id="las_2020",
            client_id="client_id",
            client_secret=SecretStr("client_secret"),
            tenant_id="tenant_id",
            graph_api_url="https://graph.microsoft.com/v1.0",
            scope="https://graph.microsoft.com/.default",
            token_url="some_url",
        )
        cls.client = SharePointClient.from_settings(cls.settings)
        cls.client.get_access_token = MagicMock(return_value="fake-token")
        with open(INTENDED_MEASUREMENTS_PATH) as f:
            cls.intended_measurements = json.load(f)

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

    def test_get_access_token_success(self):
        """Test that get_access_token returns and caches the access token."""

        client = SharePointClient.from_settings(self.settings)
        # Ensure no token is cached initially.
        client._access_token = None
        fake_token = "abc123"
        fake_response = MagicMock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = {"access_token": fake_token}

        with patch("requests.post", return_value=fake_response) as mock_post:
            token = client.get_access_token()
            self.assertEqual(token, fake_token)
            token2 = client.get_access_token()
            self.assertEqual(token2, fake_token)
            self.assertEqual(mock_post.call_count, 1)

    def test_get_access_token_failure(self):
        """Test that get_access_token raises RuntimeError when
        the GET request fails."""
        client = SharePointClient.from_settings(self.settings)
        client._access_token = None
        with patch("requests.get") as mock_get:
            fake_response = MagicMock()
            fake_response.raise_for_status.side_effect = (
                requests.exceptions.RequestException("Error")
            )
            mock_get.return_value = fake_response
            with self.assertRaises(RuntimeError) as context:
                client.get_access_token()
            self.assertIn(
                "Failed to authenticate with SharePoint",
                str(context.exception),
            )

    def test_get_headers(self):
        """Test that _get_headers constructs the correct headers
        using the access token."""
        client = SharePointClient.from_settings(self.settings)
        client.get_access_token = MagicMock(return_value="mytoken")
        headers = client._get_headers()
        expected_headers = {
            "Authorization": "Bearer mytoken",
            "Content-Type": "application/json",
        }
        self.assertEqual(headers, expected_headers)

    def test_fetch_list_items_success(self):
        """Test that JSON is returned from successful GET call."""
        client = SharePointClient.from_settings(self.settings)
        # Patch _get_headers to return a fixed header.
        client._get_headers = MagicMock(
            return_value={
                "Authorization": "Bearer fake",
                "Content-Type": "application/json",
            }
        )
        fake_json = {"value": [{"fields": {"some": "data"}}]}
        fake_response = MagicMock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = fake_json

        with patch("requests.get", return_value=fake_response) as mock_get:
            site_id = "aind_site_123"
            list_id = "nsb_2019"
            subject_id = "12345"
            subject_alias = "lab_tracks_id"
            result = client._fetch_list_items(
                site_id, list_id, subject_id, subject_alias
            )
            self.assertEqual(result, fake_json)
            expected_url = (
                f"{client.graph_api_url}/sites/{site_id}/lists/{list_id}/items"
            )
            expected_params = {
                "expand": "fields",
                "$filter": f"fields/{subject_alias} eq '{subject_id}'",
            }
            mock_get.assert_called_once_with(
                expected_url,
                headers={
                    "Authorization": "Bearer fake",
                    "Content-Type": "application/json",
                },
                params=expected_params,
            )

    def test_fetch_list_items_failure(self):
        """Test that _fetch_list_items raises error when GET call fails."""
        client = SharePointClient.from_settings(self.settings)
        client._get_headers = MagicMock(
            return_value={
                "Authorization": "Bearer fake",
                "Content-Type": "application/json",
            }
        )
        with patch(
            "requests.get",
            side_effect=requests.exceptions.RequestException("Error"),
        ):
            site_id = "aind_site_123"
            list_id = "nsb_2019"
            subject_id = "12345"
            subject_alias = "lab_tracks_id"
            with self.assertRaises(RuntimeError) as context:
                client._fetch_list_items(
                    site_id, list_id, subject_id, subject_alias
                )
            self.assertIn(
                f"Failed to fetch list items for list {list_id}.",
                str(context.exception),
            )

    def test_fetch_all_list_items_success(self):
        """Test that list is returned from successful GET call."""

        client = SharePointClient.from_settings(self.settings)
        client._get_headers = MagicMock(
            return_value={
                "Authorization": "Bearer fake",
                "Content-Type": "application/json",
            }
        )
        fake_paginated_items = [
            {"fields": {"Title": "000000 000001", "some": "data"}},
            {"fields": {"Title": "111111", "some": "data2"}},
            {"fields": {"Title": "000000 000002", "some": "data3"}},
        ]
        with patch.object(
            client, "_paginate", return_value=iter(fake_paginated_items)
        ) as mock_paginate:
            site_id = "aind_site_123"
            list_id = "las_2020"
            subject_id = "000000"

            result = client._fetch_all_list_items(
                site_id=site_id, list_id=list_id, subject_id=subject_id
            )
            expected_result = [
                {"fields": {"Title": "000000 000001", "some": "data"}},
                {"fields": {"Title": "000000 000002", "some": "data3"}},
            ]
            self.assertEqual(result, expected_result)

            expected_url = (
                f"{client.graph_api_url}/sites/{site_id}/lists/{list_id}/items"
            )
            expected_params = {
                "expand": "fields",
                "$filter": "fields/ReqPro1 eq 'Retro-Orbital Injection'",
            }
            mock_paginate.assert_called_once()
            called_kwargs = mock_paginate.call_args.kwargs
            self.assertEqual(called_kwargs.get("url"), expected_url)
            self.assertEqual(called_kwargs.get("params"), expected_params)
            self.assertIn("session", called_kwargs)

    def test_paginate(self):
        """Tests that _paginate properly iterates through paginated data."""

        client = SharePointClient.from_settings(self.settings)
        initial_url = (
            f"{client.graph_api_url}/sites/aind_site_123/lists/las_2020/items"
        )
        initial_params = {
            "expand": "fields",
            "$filter": "fields/ReqPro1 eq 'Retro-Orbital Injection'",
        }
        fake_response1 = MagicMock()
        fake_response1.raise_for_status.return_value = None
        fake_response1.json.return_value = {
            "value": [{"id": 1}, {"id": 2}],
            "@odata.nextLink": f"{initial_url}?page=2",
        }
        # response from the second page
        fake_response2 = MagicMock()
        fake_response2.raise_for_status.return_value = None
        fake_response2.json.return_value = {
            "value": [{"id": 3}],
        }
        fake_session = MagicMock()
        fake_session.get.side_effect = [fake_response1, fake_response2]
        results = list(
            SharePointClient._paginate(
                initial_url, initial_params, fake_session
            )
        )
        expected_results = [{"id": 1}, {"id": 2}, {"id": 3}]
        self.assertEqual(results, expected_results)
        expected_calls = [
            call(initial_url, params=initial_params),
            call(f"{initial_url}?page=2", params=None),
        ]
        fake_session.get.assert_has_calls(expected_calls)

    def test_empty_response(self):
        """Tests that an empty response is generated if no data returned
        from NSB datatbases"""
        with patch.object(
            self.client, "_fetch_list_items", return_value={"value": []}
        ):
            response = self.client.get_procedure_info(
                subject_id="12345", list_id="nsb_2019"
            )

        self.assertEqual(StatusCodes.DB_RESPONDED, response.status_code)
        self.assertEqual([], response.aind_models)
        json_response = response.map_to_json_response()
        self.assertEqual(
            StatusCodes.NO_DATA_FOUND.value, json_response.status_code
        )

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
                {"value": [{"fields": list_item_2023_raw}]},
            ],
        ):
            with patch.object(
                self.client,
                "_extract_procedures_from_response",
                side_effect=[
                    expected_mapped_2019,
                    expected_mapped_2023,
                    expected_mapped_2023,
                ],
            ):
                response2019 = self.client.get_procedure_info(
                    subject_id="12345", list_id="nsb_2019"
                )
                response2023 = self.client.get_procedure_info(
                    subject_id="12345", list_id="nsb_2023"
                )
                response2025 = self.client.get_procedure_info(
                    subject_id="12345", list_id="nsb_present"
                )
        merged_response = self.client.merge_responses(
            [response2019, response2023, response2025]
        )
        json_response = merged_response.map_to_json_response()
        actual_content = json.loads(json_response.body.decode("utf-8"))
        actual_subject_procedures = actual_content["data"][
            "subject_procedures"
        ]
        # Duplicate models should be removed
        expected_subject_procedures = (
            expected_mapped_2019 + expected_mapped_2023
        )
        expected_subject_procedures.sort(key=lambda x: str(x))
        actual_subject_procedures.sort(key=lambda x: str(x))
        self.assertEqual(StatusCodes.DB_RESPONDED, merged_response.status_code)
        self.assertEqual(406, json_response.status_code)
        self.assertEqual(
            expected_subject_procedures, actual_subject_procedures
        )

    def test_las_data_mapped(self):
        """Tests that 200 response returned correctly."""
        list_item_2020_raw = self.list_items_2020[0][0]
        expected_mapped_2020 = self.list_items_2020[0][1]

        # Patch _fetch_list_items to simulate the Graph API response for LAS.
        with patch.object(
            self.client,
            "_fetch_all_list_items",
            return_value=[list_item_2020_raw],
        ):
            with patch.object(
                self.client,
                "_extract_procedures_from_response",
                return_value=expected_mapped_2020,
            ):
                response = self.client.get_procedure_info(
                    subject_id="000000", list_id="las_2020"
                )

        self.assertEqual(StatusCodes.DB_RESPONDED, response.status_code)
        json_response = response.map_to_json_response()
        actual_content = json.loads(json_response.body.decode("utf-8"))
        actual_subject_procedures = actual_content["data"][
            "subject_procedures"
        ]
        self.assertEqual(expected_mapped_2020, actual_subject_procedures)
        self.assertEqual(406, json_response.status_code)

    def test_intended_measurement_data_mapped(self):
        """Tests that 200 response returned correctly."""
        list_item_raw = self.intended_measurements
        expected_mapped_data = [
            {
                "fiber_name": None,
                "intended_measurement_R": "acetylcholine",
                "intended_measurement_G": "calcium",
                "intended_measurement_B": "GABA",
                "intended_measurement_Iso": "control",
            },
            {
                "fiber_name": "Fiber_0",
                "intended_measurement_R": "acetylcholine",
                "intended_measurement_G": "dopamine",
                "intended_measurement_B": "GABA",
                "intended_measurement_Iso": "control",
            },
            {
                "fiber_name": "Fiber_1",
                "intended_measurement_R": "acetylcholine",
                "intended_measurement_G": "dopamine",
                "intended_measurement_B": "glutamate",
                "intended_measurement_Iso": "control",
            },
            {
                "fiber_name": "Fiber_0",
                "intended_measurement_R": "norepinephrine",
                "intended_measurement_G": "calcium",
                "intended_measurement_B": "glutamate",
                "intended_measurement_Iso": "voltage",
            },
        ]
        with patch.object(
            self.client,
            "_fetch_list_items",
            return_value={"value": [{"fields": list_item_raw}]},
        ):
            with patch.object(
                self.client,
                "_extract_procedures_from_response",
                return_value=expected_mapped_data,
            ):
                response = self.client.get_intended_measurement_info(
                    subject_id="000000"
                )
        self.assertEqual(StatusCodes.DB_RESPONDED, response.status_code)
        json_response = response.map_to_json_response()
        actual_content = json.loads(json_response.body.decode("utf-8"))
        self.assertEqual(expected_mapped_data, actual_content["data"])
        self.assertEqual(300, json_response.status_code)

    def test_get_intended_measurement_info_error(self):
        """Tests internal server error response caught correctly."""
        with patch.object(
            self.client,
            "_fetch_list_items",
            side_effect=BrokenPipeError("BrokenPipeError()"),
        ):
            response2023_error = self.client.get_intended_measurement_info(
                subject_id="12345"
            )
        self.assertEqual(
            response2023_error.status_code, StatusCodes.INTERNAL_SERVER_ERROR
        )

    def test_merge_empty_procedures(self):
        """Tests that merging empty responses returns Internal Server Error."""

        response = self.client.merge_responses(model_responses=[])
        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR, response.status_code
        )

    def test_merge_valid_empty_procedures(self):
        """
        Test that merging a valid NSB 2019 response (using JSON file data)
        with an empty response returns the valid procedures.
        """
        raw_2019 = self.list_items_2019[0][0]
        expected_mapped = self.list_items_2019[0][1]
        with patch.object(
            self.client,
            "_fetch_list_items",
            return_value={"value": [{"fields": raw_2019}]},
        ):
            with patch.object(
                self.client,
                "_extract_procedures_from_response",
                return_value=expected_mapped,
            ):
                response2019 = self.client.get_procedure_info(
                    subject_id="12345", list_id="nsb_2019"
                )
        response_empty = ModelResponse(
            aind_models=[], status_code=StatusCodes.DB_RESPONDED
        )
        expected_subject_procedures = expected_mapped
        merged_left = self.client.merge_responses(
            [response2019, response_empty]
        )
        merged_right = self.client.merge_responses(
            [response_empty, response2019]
        )
        json_response_left = merged_left.map_to_json_response()
        actual_content_left = json.loads(
            json_response_left.body.decode("utf-8")
        )
        actual_subject_procedures_left = actual_content_left["data"][
            "subject_procedures"
        ]

        json_response_right = merged_right.map_to_json_response()
        actual_content_right = json.loads(
            json_response_right.body.decode("utf-8")
        )
        actual_subject_procedures_right = actual_content_right["data"][
            "subject_procedures"
        ]

        expected_subject_procedures.sort(key=lambda x: str(x))
        actual_subject_procedures_left.sort(key=lambda x: str(x))
        actual_subject_procedures_right.sort(key=lambda x: str(x))
        self.assertEqual(StatusCodes.DB_RESPONDED, merged_left.status_code)
        self.assertEqual(406, json_response_left.status_code)
        self.assertEqual(
            expected_subject_procedures, actual_subject_procedures_left
        )
        self.assertEqual(StatusCodes.DB_RESPONDED, merged_right.status_code)
        self.assertEqual(406, json_response_right.status_code)
        self.assertEqual(
            expected_subject_procedures, actual_subject_procedures_right
        )

    def test_merge_valid_error_procedures(self):
        """Tests that merging valid and error responses returned correctly."""

        raw_2019 = self.list_items_2019[0][0]
        expected_mapped = self.list_items_2019[0][1]
        with patch.object(
            self.client,
            "_fetch_list_items",
            return_value={"value": [{"fields": raw_2019}]},
        ):
            with patch.object(
                self.client,
                "_extract_procedures_from_response",
                return_value=expected_mapped,
            ):
                response2019 = self.client.get_procedure_info(
                    subject_id="12345", list_id="nsb_2019"
                )
        # simulate an error
        with patch.object(
            self.client,
            "_fetch_list_items",
            side_effect=BrokenPipeError("BrokenPipeError()"),
        ):
            response2023_error = self.client.get_procedure_info(
                subject_id="12345", list_id="nsb_2023"
            )
        merged = self.client.merge_responses(
            [response2023_error, response2019]
        )
        json_response = merged.map_to_json_response()
        actual_content = json.loads(json_response.body.decode("utf-8"))
        actual_subject_procedures = actual_content["data"][
            "subject_procedures"
        ]
        expected_subject_procedures = expected_mapped
        expected_subject_procedures.sort(key=lambda x: str(x))
        actual_subject_procedures.sort(key=lambda x: str(x))

        self.assertEqual(StatusCodes.MULTI_STATUS, merged.status_code)
        self.assertEqual(207, json_response.status_code)
        self.assertEqual(
            expected_subject_procedures, actual_subject_procedures
        )
        with patch("logging.error") as mock_log:
            try:
                raise BrokenPipeError("BrokenPipeError()")
            except Exception:
                pass
            mock_log.assert_not_called()

    def test_merge_three_responses(self):
        """Tests that multi status is returned as expected."""

        response1 = ModelResponse.internal_server_error_response()
        response2 = ModelResponse.internal_server_error_response()
        raw_2019 = self.list_items_2019[0][0]
        mapped_2019 = self.list_items_2019[0][1]
        with patch.object(
            self.client,
            "_fetch_list_items",
            return_value={"value": [{"fields": raw_2019}]},
        ):
            with patch.object(
                self.client,
                "_extract_procedures_from_response",
                return_value=mapped_2019,
            ):
                response3 = self.client.get_procedure_info(
                    subject_id="12345", list_id="nsb_2019"
                )

        merged = self.client.merge_responses([response1, response2, response3])
        json_response = merged.map_to_json_response()
        body = json.loads(json_response.body.decode("utf-8"))

        self.assertEqual(StatusCodes.MULTI_STATUS, merged.status_code)
        self.assertEqual(207, json_response.status_code)
        self.assertEqual(
            "There was an error retrieving records from one or more "
            "of the databases.",
            body.get("message"),
        )
        proc = response3.aind_models[0]
        expected_data = json.loads(proc.model_dump_json())
        self.assertEqual(expected_data, body.get("data"))

    def test_merge_error_responses(self):
        """Tests that merging error responses returns internal server error."""

        response1 = ModelResponse.internal_server_error_response()
        response2 = ModelResponse.connection_error_response()
        merged_responses = self.client.merge_responses([response1, response2])
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

    @patch("logging.error")
    def test_error_response(
        self,
        mock_log: MagicMock,
    ):
        """Tests internal server error response caught correctly."""

        with patch.object(
            self.client,
            "_fetch_list_items",
            side_effect=Exception("Test error"),
        ):
            response = self.client.get_procedure_info(
                subject_id="12345", list_id="nsb_2023"
            )
        mock_log.assert_called_once()  # Ensure error was logged.
        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR, response.status_code
        )
        self.assertEqual([], response.aind_models)
        json_response = response.map_to_json_response()
        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR.value, json_response.status_code
        )
        body = json.loads(json_response.body.decode("utf-8"))
        self.assertIsNone(body.get("data"))

    def test_corrupt_list_title(self):
        """Tests that an error is logged if a corrupt list title is input."""

        response = self.client.get_procedure_info(
            subject_id="12345", list_id="unknown_list"
        )
        expected = ModelResponse.internal_server_error_response()
        self.assertEqual(expected.status_code, response.status_code)
        self.assertEqual([], response.aind_models)

    def test_handle_duplicates(self):
        """Tests that duplicates are removed as expected."""
        # Test duplicate dictionaries
        item1 = {"id": 1, "name": "Alice"}
        item2 = {"name": "Alice", "id": 1}
        item3 = {"id": 2, "name": "Bob"}
        result = self.client._handle_duplicates([item1, item2, item3])
        self.assertEqual(result, [item1, item3])

        # Test unsupported item type
        with self.assertRaises(TypeError) as context:
            self.client._handle_duplicates([{"id": 1}, 42])

        self.assertIn("Unsupported item type", str(context.exception))


if __name__ == "__main__":
    unittest.main()
