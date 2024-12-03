"""Tests methods in route module."""

from unittest.mock import patch

import pytest
from aind_data_schema.core.procedures import ViralMaterial

from aind_metadata_service.backends.tars.models import (
    Alias,
    MoleculeData,
    PrepLotData,
    ViralPrep,
    Virus,
)


class TestRoute:
    """Test injection_materials responses."""

    def test_get_200_inj_materials(
        self,
        client,
        mock_get_raw_prep_lot_response,
        mock_get_raw_molecule_response,
        mock_get_access_token,
    ):
        """Tests a good response"""

        response = client.get("/injection_materials/VT3214g")
        assert 200 == response.status_code

    def test_get_404_inj_materials(
        self,
        client,
        mock_get_raw_prep_lot_response,
        mock_get_raw_molecule_response,
        mock_get_access_token,
    ):
        """Tests a missing response"""

        response = client.get("/injection_materials/none_such_id")
        assert 404 == response.status_code

    def test_500_internal_server_error(
        self,
        client,
        mock_get_raw_prep_lot_response,
        mock_get_raw_molecule_response,
        mock_get_access_token,
        caplog,
    ):
        """Tests an internal server error response"""

        with patch(
            "aind_metadata_service.backends.tars.handler.SessionHandler"
            ".get_prep_lot_data",
            side_effect=Exception("Something went wrong"),
        ):
            response = client.get("/injection_materials/VT3214g")

        expected_response = {"message": "Internal Server Error", "data": None}
        assert 500 == response.status_code
        assert expected_response == response.json()
        assert "An error occurred: ('Something went wrong',)" in caplog.text

    def test_200_model2(
        self,
        client,
        mock_get_raw_prep_lot_response,
        mock_get_raw_molecule_response,
        mock_get_access_token,
    ):
        """Tests another valid model response"""

        example_prep_lot_data = PrepLotData(
            lot="VT3214g",
            viralPrep=ViralPrep(virus=Virus(aliases=[Alias(name="AiP123")])),
        )
        example_molecule_data = MoleculeData(
            aliases=[Alias(name="AiP123"), Alias(name="something")]
        )
        with patch(
            "aind_metadata_service.backends.tars.handler.SessionHandler"
            ".get_prep_lot_data",
            return_value=[example_prep_lot_data],
        ):
            with patch(
                "aind_metadata_service.backends.tars.handler.SessionHandler"
                ".get_molecule_data",
                return_value=[example_molecule_data],
            ):
                response = client.get("/injection_materials/VT3214g")

        assert 200 == response.status_code

    def test_406_model(
        self,
        client,
        mock_get_raw_prep_lot_response,
        mock_get_raw_molecule_response,
        mock_get_access_token,
    ):
        """Tests another valid model response"""

        example_viral_material = ViralMaterial.model_construct(name=None)
        with patch(
            "aind_metadata_service.routers.injection_materials.mapper.Mapper"
            ".map_to_viral_material",
            return_value=example_viral_material,
        ):
            response = client.get("/injection_materials/VT3214g")

        assert 406 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
