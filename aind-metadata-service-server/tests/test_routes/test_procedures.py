"""Tests procedures route"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from aind_labtracks_service_async_client.models import Task as LabTracksTask
from aind_sharepoint_service_async_client.models import (
    NSB2023List,
)
from aind_smartsheet_service_async_client.models import ProtocolsModel
from fastapi.testclient import TestClient


class TestRoute:
    """Test responses."""

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2023")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb_present")
    @patch(
        "aind_slims_service_async_client.DefaultApi.get_water_restriction_data"
    )
    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    @patch("aind_tars_service_async_client.DefaultApi.get_viral_prep_lots")
    @patch("aind_tars_service_async_client.DefaultApi.get_viruses")
    def test_get_procedures_valid_data_only_labtracks(
        self,
        mock_get_viruses: AsyncMock,
        mock_get_viral_prep_lots: AsyncMock,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
        mock_get_histology: AsyncMock,
        mock_get_water_restriction: AsyncMock,
        mock_nsb_present: AsyncMock,
        mock_nsb2023: AsyncMock,
        mock_nsb2019: AsyncMock,
        mock_las: AsyncMock,
        mock_labtracks: AsyncMock,
        client: TestClient,
    ):
        """Tests successful retrieval of procedures"""
        mock_labtracks.return_value = [
            LabTracksTask(
                id="00000",
                type_name="Perfusion Gel",
                date_start=datetime(2022, 10, 11, 0, 0),
                date_end=datetime(2022, 10, 11, 4, 30),
                investigator_id="28803",
                task_object="000000",
                protocol_number="2002",
                task_status="F",
            )
        ]
        mock_las.return_value = []
        mock_nsb2019.return_value = []
        mock_get_perfusions.return_value = []
        mock_get_protocols.return_value = [
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Perfusion",
                protocol_name=(
                    "Mouse Cardiac Perfusion Fixation and Brain Collection V.5"
                ),
                doi="dx.doi.org/10.17504/protocols.io.test",
                version="1.0",
            )
        ]
        mock_nsb2023.return_value = []
        mock_nsb_present.return_value = []
        mock_get_water_restriction.return_value = []
        mock_get_histology.return_value = []
        mock_get_viral_prep_lots.return_value = []
        mock_get_viruses.return_value = []

        response = client.get("api/v2/procedures/000000")
        assert response.status_code == 200

        mock_labtracks.assert_called_once()
        mock_las.assert_called_once()
        mock_nsb2019.assert_called_once()
        mock_nsb2023.assert_called_once()
        mock_nsb_present.assert_called_once()
        mock_get_water_restriction.assert_called_once()
        mock_get_histology.assert_called_once()
        mock_get_perfusions.assert_called_once()
        assert mock_get_protocols.call_count >= 1

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2023")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb_present")
    @patch(
        "aind_slims_service_async_client.DefaultApi.get_water_restriction_data"
    )
    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    @patch("aind_tars_service_async_client.DefaultApi.get_viral_prep_lots")
    @patch("aind_tars_service_async_client.DefaultApi.get_viruses")
    def test_get_procedures_invalid_data(
        self,
        mock_get_viruses: AsyncMock,
        mock_get_viral_prep_lots: AsyncMock,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
        mock_get_histology: AsyncMock,
        mock_get_water_restriction: AsyncMock,
        mock_nsb_present: AsyncMock,
        mock_nsb2023: AsyncMock,
        mock_nsb2019: AsyncMock,
        mock_las: AsyncMock,
        mock_labtracks: AsyncMock,
        client: TestClient,
        recwarn: pytest.WarningsRecorder,
        mock_tars_prep_lot_230929,
        mock_tars_virus_v123,
    ):
        """
        Tests a procedures model is built as best as possible even with
        missing data, verifies serialization warnings are issued, and
        confirms concurrent API calls across all three batches.
        """
        mock_labtracks.return_value = [
            LabTracksTask(
                id="00000",
                type_name="Perfusion Gel",
                date_start=datetime(2022, 10, 11, 0, 0),
                date_end=datetime(2022, 10, 11, 4, 30),
                investigator_id="28803",
                task_object="000000",
                protocol_number="2002",
                task_status="F",
            )
        ]
        mock_las.return_value = []
        mock_get_protocols.return_value = []
        mock_get_perfusions.return_value = []
        mock_get_water_restriction.return_value = []
        mock_get_histology.return_value = []
        mock_get_viral_prep_lots.return_value = [mock_tars_prep_lot_230929]
        mock_get_viruses.return_value = [mock_tars_virus_v123]
        mock_nsb2019.return_value = []
        mock_nsb2023.return_value = [
            NSB2023List(
                Date_x0020_of_x0020_Surgery="2022-01-03T00:00:00Z",
                Weight_x0020_before_x0020_Surger=25.2,
                Weight_x0020_after_x0020_Surgery=28.2,
                HpWorkStation="SWS 4",
                IACUC_x0020_Protocol_x0020__x002="2103",
                Headpost="Visual Ctx",
                HeadpostType="Mesoscope",
                Headpost_x0020_Perform_x0020_Dur="Initial Surgery",
                CraniotomyType="5mm",
                Craniotomy_x0020_Perform_x0020_D="Initial Surgery",
                Procedure="Sx-01 Visual Ctx 2P",
                Test1LookupId=2846,
                Breg2Lamb=4.5,
                Iso_x0020_On=1.5,
                HPIsoLevel=2.0,
                HPRecovery=25,
                Burr_x0020_hole_x0020_1="Injection",
                Burr1_x0020_Perform_x0020_During="Initial Surgery",
                Virus_x0020_M_x002f_L=2.0,
                Virus_x0020_A_x002f_P=-1.5,
                Virus_x0020_D_x002f_V=3.0,
                Virus_x0020_Hemisphere="Right",
                Inj1Type="Nanoject (Pressure)",
                inj1volperdepth=500.0,
                Burr_x0020_1_x0020_Injectable_x0="230929-12",
                Burr_x0020_1_x0020_Injectable_x03="1e12",
                Inj1VirusStrain_rt='Premixed "dL+Cre"',
            )
        ]
        mock_nsb_present.return_value = []

        response = client.get("api/v2/procedures/000000")
        assert response.status_code == 400
        assert len(recwarn) == 1
        w = recwarn.pop()
        assert issubclass(w.category, UserWarning)
        assert "Pydantic serializer warnings" in str(w.message)

        mock_labtracks.assert_called_once()
        mock_las.assert_called_once()
        mock_nsb2019.assert_called_once()
        mock_nsb2023.assert_called_once()
        mock_nsb_present.assert_called_once()
        mock_get_water_restriction.assert_called_once()
        mock_get_histology.assert_called_once()
        mock_get_perfusions.assert_called_once()
        assert mock_get_protocols.call_count >= 1
        mock_get_viral_prep_lots.assert_called_once_with(
            lot="230929-12", _request_timeout=10
        )
        mock_get_viruses.assert_called_once_with(
            name="v_123", _request_timeout=10
        )

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2023")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb_present")
    @patch(
        "aind_slims_service_async_client.DefaultApi.get_water_restriction_data"
    )
    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    @patch("aind_tars_service_async_client.DefaultApi.get_viral_prep_lots")
    @patch("aind_tars_service_async_client.DefaultApi.get_viruses")
    def test_get_procedures_no_data(
        self,
        mock_get_viruses: AsyncMock,
        mock_get_viral_prep_lots: AsyncMock,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
        mock_get_histology: AsyncMock,
        mock_get_water_restriction: AsyncMock,
        mock_nsb_present: AsyncMock,
        mock_nsb2023: AsyncMock,
        mock_nsb2019: AsyncMock,
        mock_las: AsyncMock,
        mock_labtracks: AsyncMock,
        client: TestClient,
    ):
        """Tests no data found and verifies concurrent API calls."""
        mock_labtracks.return_value = []
        mock_las.return_value = []
        mock_nsb2019.return_value = []
        mock_get_perfusions.return_value = []
        mock_get_protocols.return_value = []
        mock_nsb2023.return_value = []
        mock_nsb_present.return_value = []
        mock_get_water_restriction.return_value = []
        mock_get_histology.return_value = []
        mock_get_viral_prep_lots.return_value = []
        mock_get_viruses.return_value = []

        response = client.get("api/v2/procedures/nonexistent_subject")
        assert response.status_code == 404

    @patch("aind_labtracks_service_async_client.DefaultApi.get_tasks")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_las2020")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2019")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb2023")
    @patch("aind_sharepoint_service_async_client.DefaultApi.get_nsb_present")
    @patch(
        "aind_slims_service_async_client.DefaultApi.get_water_restriction_data"
    )
    @patch("aind_slims_service_async_client.DefaultApi.get_histology_data")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_perfusions")
    @patch("aind_smartsheet_service_async_client.DefaultApi.get_protocols")
    @patch("aind_tars_service_async_client.DefaultApi.get_viral_prep_lots")
    @patch("aind_tars_service_async_client.DefaultApi.get_viruses")
    def test_get_procedures_virus_strain_not_found_in_tars(
        self,
        mock_get_viruses: AsyncMock,
        mock_get_viral_prep_lots: AsyncMock,
        mock_get_protocols: AsyncMock,
        mock_get_perfusions: AsyncMock,
        mock_get_histology: AsyncMock,
        mock_get_water_restriction: AsyncMock,
        mock_nsb_present: AsyncMock,
        mock_nsb2023: AsyncMock,
        mock_nsb2019: AsyncMock,
        mock_las: AsyncMock,
        mock_labtracks: AsyncMock,
        client: TestClient,
    ):
        """Tests handling when virus strain is not found in TARS."""
        mock_labtracks.return_value = []
        mock_las.return_value = []
        mock_get_perfusions.return_value = []
        mock_get_protocols.return_value = []
        mock_get_water_restriction.return_value = []
        mock_get_histology.return_value = []
        mock_get_viral_prep_lots.return_value = []
        mock_get_viruses.return_value = []

        mock_nsb2019.return_value = []
        mock_nsb2023.return_value = [
            NSB2023List(
                Date_x0020_of_x0020_Surgery="2022-01-03T00:00:00Z",
                Weight_x0020_before_x0020_Surger=25.2,
                Weight_x0020_after_x0020_Surgery=28.2,
                HpWorkStation="SWS 4",
                IACUC_x0020_Protocol_x0020__x002="2103",
                Headpost="Visual Ctx",
                HeadpostType="Mesoscope",
                Headpost_x0020_Perform_x0020_Dur="Initial Surgery",
                CraniotomyType="5mm",
                Craniotomy_x0020_Perform_x0020_D="Initial Surgery",
                Procedure="Sx-01 Visual Ctx 2P",
                Test1LookupId=2846,
                Breg2Lamb=4.5,
                Iso_x0020_On=1.5,
                HPIsoLevel=2.0,
                HPRecovery=25,
                Burr_x0020_hole_x0020_1="Injection",
                Burr1_x0020_Perform_x0020_During="Initial Surgery",
                Virus_x0020_M_x002f_L=2.0,
                Virus_x0020_A_x002f_P=-1.5,
                Virus_x0020_D_x002f_V=3.0,
                Virus_x0020_Hemisphere="Right",
                Inj1Type="Nanoject (Pressure)",
                inj1volperdepth=500.0,
                Burr_x0020_1_x0020_Injectable_x0="UNKNOWN-VIRUS-123",
                Burr_x0020_1_x0020_Injectable_x03="1e12",
                Inj1VirusStrain_rt="Unknown strain",
            )
        ]
        mock_nsb_present.return_value = []

        response = client.get("api/v2/procedures/000000")
        assert response.status_code == 200
        assert mock_get_viral_prep_lots.call_count == 1
        mock_get_viral_prep_lots.assert_called_with(
            lot="UNKNOWN-VIRUS-123", _request_timeout=10
        )
        assert mock_get_viruses.call_count == 0


if __name__ == "__main__":
    pytest.main([__file__])
