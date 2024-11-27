""""Tests response_handler module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aind_data_schema.core.procedures import Procedures
from aind_data_schema.core.subject import BreedingInfo, Species, Subject
from aind_data_schema_models.organizations import Organization
from aind_metadata_mapper.core import JobResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from aind_metadata_service.response_handler import (
    EtlResponse,
    ModelResponse,
    StatusCodes,
)

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
DIR_MAP = TEST_DIR / "resources" / "json_responses"

SP_VALID_RESPONSE_PATH = DIR_MAP / "mapped_sp_procedure.json"
LAS_VALID_RESPONSE_PATH = DIR_MAP / "mapped_las_procedure.json"
COMBINED_VALID_PATH = DIR_MAP / "combined.json"

SP_INVALID_RESPONSE_PATH = DIR_MAP / "mapped_sp_procedure_invalid.json"
LAS_INVALID_RESPONSE_PATH = DIR_MAP / "mapped_las_procedure_invalid.json"
COMBINED_INVALID_PATH = DIR_MAP / "combined_invalid.json"

with open(SP_VALID_RESPONSE_PATH) as f:
    sp_valid_subject_procedures = json.load(f)

with open(LAS_VALID_RESPONSE_PATH) as f:
    las_valid_subject_procedures = json.load(f)

with open(COMBINED_VALID_PATH) as f:
    combined_valid_procedures = json.load(f)

with open(SP_INVALID_RESPONSE_PATH) as f:
    sp_invalid_subject_procedures = json.load(f)

with open(LAS_INVALID_RESPONSE_PATH) as f:
    las_invalid_subject_procedures = json.load(f)

with open(COMBINED_INVALID_PATH) as f:
    combined_invalid_procedures = json.load(f)

sp_valid_model = Procedures.model_construct(
    subject_id="115977",
    subject_procedures=sp_valid_subject_procedures["data"][
        "subject_procedures"
    ],
)
lb_valid_model = Procedures.model_construct(
    subject_id="115977",
    subject_procedures=las_valid_subject_procedures["data"][
        "subject_procedures"
    ],
)
sp_invalid_model = Procedures.model_construct(
    subject_id="115977",
    subject_procedures=sp_invalid_subject_procedures["data"][
        "subject_procedures"
    ],
)
lb_invalid_model = Procedures.model_construct(
    subject_id="115977",
    subject_procedures=las_invalid_subject_procedures["data"][
        "subject_procedures"
    ],
)


class TestResponseHandler(unittest.TestCase):
    """Tests JSON methods in Responses class"""

    def test_valid_model(self):
        """Test model_response with valid model."""

        model = Subject(
            species=Species.MUS_MUSCULUS,
            source=Organization.AI,
            breeding_info=BreedingInfo(
                breeding_group="C57BL6J_OLD",
                maternal_id="107392",
                maternal_genotype="wt/wt",
                paternal_id="107384",
                paternal_genotype="Adora2a-Cre/wt",
            ),
            subject_id="639374",
            sex="Male",
            date_of_birth="2022-06-24",
            genotype="Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
        )
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        actual_json = model_response.map_to_json_response()

        model_json = jsonable_encoder(json.loads(model.model_dump_json()))
        expected_json = JSONResponse(
            status_code=200,
            content=(
                {
                    "message": "Valid Model.",
                    "data": model_json,
                }
            ),
        )

        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_invalid_model(self):
        """Test model_response with invalid model."""
        model = Subject.model_construct()
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        actual_json = model_response.map_to_json_response()

        validation_error = None
        try:
            model.__class__.model_validate(model.model_dump())
        except ValidationError as e:
            validation_error = repr(e)

        model_json = jsonable_encoder(model)
        expected_json = JSONResponse(
            status_code=406,
            content=(
                {
                    "message": f"Validation Errors: {validation_error}",
                    "data": model_json,
                }
            ),
        )
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    @patch("aind_metadata_service.response_handler.json.loads")
    @patch("aind_metadata_service.response_handler.Subject.model_validate")
    def test_key_error(self, mock_model_validate, mock_json_loads):
        """Test model_response with valid model."""
        key_error = KeyError("Mocked Key Error")
        mock_model_validate.side_effect = key_error
        mock_json_loads.return_value = {"invalid_key": "value"}
        aind_model = MagicMock(spec=Subject)
        aind_model.model_dump.return_value = "{}"
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[aind_model]
        )
        actual_json = model_response.map_to_json_response()
        expected_json = JSONResponse(
            status_code=406,
            content=(
                {
                    "message": f"Validation Errors: KeyError({key_error})",
                    "data": {"invalid_key": "value"},
                }
            ),
        )
        self.assertEqual(
            actual_json.status_code, StatusCodes.INVALID_DATA.value
        )
        self.assertEqual(actual_json.body, expected_json.body)

    def test_no_validation(self):
        """Test model_response when validation is turned off."""
        model = Subject.model_construct()
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        actual_json = model_response.map_to_json_response(validate=False)
        model_json = jsonable_encoder(model)
        expected_json = JSONResponse(
            status_code=422,
            content=(
                {
                    "message": "Valid Request Format. "
                    "Models have not been validated.",
                    "data": model_json,
                }
            ),
        )

        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_multiple_items_response(self):
        """Test multiple item response with validation."""
        models = [sp_valid_model, sp_valid_model]
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=models
        )
        actual_json = model_response.map_to_json_response()

        models_json = [
            jsonable_encoder(json.loads(model.model_dump_json()))
            for model in models
        ]
        validation_error = ModelResponse._validate_model(sp_valid_model)
        expected_json = JSONResponse(
            status_code=300,
            content=(
                {
                    "message": f"Multiple Items Found. Validation Errors:"
                    f" {validation_error}, {validation_error}",
                    "data": models_json,
                }
            ),
        )

        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_multiple_items_response_no_validation(self):
        """Test multiple item response"""
        models = [sp_valid_model, sp_valid_model]
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=models
        )
        actual_json = model_response.map_to_json_response(validate=False)

        models_json = [
            jsonable_encoder(json.loads(model.model_dump_json()))
            for model in models
        ]
        expected_json = JSONResponse(
            status_code=300,
            content=(
                {
                    "message": "Multiple Items Found."
                    " Models have not been validated.",
                    "data": models_json,
                }
            ),
        )

        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_nodata_error(self):
        """Test no data error response"""
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[]
        )
        actual_json = model_response.map_to_json_response()

        expected_json = JSONResponse(
            status_code=404,
            content=(
                {
                    "message": "No Data Found.",
                    "data": None,
                }
            ),
        )
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_connection_error(self):
        """Test connection error response"""
        model_response = ModelResponse.connection_error_response()
        actual_json = model_response.map_to_json_response()

        expected_json = JSONResponse(
            status_code=503,
            content=(
                {
                    "message": "Connection Error.",
                    "data": None,
                }
            ),
        )
        self.assertEqual(
            StatusCodes.CONNECTION_ERROR, model_response.status_code
        )
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_internal_error(self):
        """Test internal error response"""
        model_response = ModelResponse.internal_server_error_response()
        actual_json = model_response.map_to_json_response()

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
            StatusCodes.INTERNAL_SERVER_ERROR, model_response.status_code
        )
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)


class TestEtlResponse(unittest.TestCase):
    """Tests methods in EtlResponse class"""

    def test_map_job_response(self):
        """Tests map_job_response method"""
        job_response = JobResponse(
            status_code=200, message="All is good!", data='{"key1":"value1"}'
        )
        json_response = EtlResponse.map_job_response(job_response)
        self.assertEqual(200, json_response.status_code)
        json_response_body = json.loads(json_response.body)
        self.assertEqual("All is good!", json_response_body["message"])
        self.assertEqual('{"key1":"value1"}', json_response_body["data"])


if __name__ == "__main__":
    unittest.main()
