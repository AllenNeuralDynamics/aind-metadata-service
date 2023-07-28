""""Tests response_handler module"""

import json
import os
import unittest
from pathlib import Path

from aind_data_schema.procedures import Procedures
from aind_data_schema.subject import Species, Subject
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import validate_model

from aind_metadata_service.response_handler import ModelResponse, StatusCodes

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

sp_valid_model = Procedures.construct(
    subject_id="115977",
    subject_procedures=sp_valid_subject_procedures["data"][
        "subject_procedures"
    ],
)
lb_valid_model = Procedures.construct(
    subject_id="115977",
    subject_procedures=las_valid_subject_procedures["data"][
        "subject_procedures"
    ],
)
sp_invalid_model = Procedures.construct(
    subject_id="115977",
    subject_procedures=sp_invalid_subject_procedures["data"][
        "subject_procedures"
    ],
)
lb_invalid_model = Procedures.construct(
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
            subject_id="639374",
            sex="Male",
            date_of_birth="2022-06-24",
            genotype="Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
        )
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        actual_json = model_response.map_to_json_response()

        model_json = jsonable_encoder(json.loads(model.json()))
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
        model = Subject.construct()
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        actual_json = model_response.map_to_json_response()

        *_, validation_error = validate_model(model.__class__, model.__dict__)
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

    def test_multiple_items_response(self):
        """Test multiple item response"""
        models = [sp_valid_model, sp_valid_model]
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=models
        )
        actual_json = model_response.map_to_json_response()

        models_json = [
            jsonable_encoder(json.loads(model.json())) for model in models
        ]
        expected_json = JSONResponse(
            status_code=300,
            content=(
                {
                    "message": "Multiple Items Found.",
                    "data": models_json,
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


if __name__ == "__main__":
    unittest.main()
