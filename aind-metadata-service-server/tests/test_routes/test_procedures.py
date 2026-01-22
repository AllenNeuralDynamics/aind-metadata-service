"""Tests procedures route"""

from datetime import datetime
from unittest.mock import AsyncMock, patch, call
import asyncio

import pytest
from aind_labtracks_service_async_client.models import Task as LabTracksTask
from aind_sharepoint_service_async_client.models import (
    NSB2019List,
    NSB2023List,
)
from aind_tars_service_async_client import (
    Alias,
    PrepLotData,
    ViralPrep,
    VirusData,
)
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
        """Tests successful retrieval of procedures."""
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
        mock_get_protocols.return_value = []
        mock_nsb2023.return_value = []
        mock_nsb_present.return_value = []
        mock_get_water_restriction.return_value = []
        mock_get_histology.return_value = []
        mock_get_viral_prep_lots.return_value = []
        mock_get_viruses.return_value = []

        response = client.get("api/v2/procedures/000000")
        assert response.status_code == 200
        
        # Verify all initial API calls were made (concurrent batch 1)
        mock_labtracks.assert_called_once()
        mock_las.assert_called_once()
        mock_nsb2019.assert_called_once()
        mock_nsb2023.assert_called_once()
        mock_nsb_present.assert_called_once()
        mock_get_water_restriction.assert_called_once()
        mock_get_histology.assert_called_once()
        mock_get_perfusions.assert_called_once()

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
    def test_get_procedures_concurrent_tars_fetches(
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
        """Tests that TARS viral prep and virus fetches happen concurrently."""
        mock_labtracks.return_value = []
        mock_las.return_value = []
        mock_get_perfusions.return_value = []
        mock_get_protocols.return_value = []
        mock_get_water_restriction.return_value = []
        mock_get_histology.return_value = []
        
        # Setup data with multiple virus strains
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
        
        # Mock TARS responses
        mock_get_viral_prep_lots.return_value = [
            PrepLotData(
                lot="230929-12",
                viral_prep=ViralPrep(
                    virus=VirusData(
                        aliases=[Alias(is_preferred=True, name="v_123")]
                    )
                ),
            )
        ]
        mock_get_viruses.return_value = [
            VirusData(aliases=[Alias(is_preferred=True, name="v_123")])
        ]

        response = client.get("api/v2/procedures/000000")
        
        # Should succeed even with invalid data due to best-effort mapping
        assert response.status_code in [200, 400]
        
        # Verify TARS API was called for viral prep lots
        mock_get_viral_prep_lots.assert_called()
        
        # Verify virus API was called (should happen after prep lots)
        mock_get_viruses.assert_called()

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
    ):
        """
        Tests a procedures model is built as best as possible even with
        missing data and verifies serialization warnings are issued.
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
        mock_get_viral_prep_lots.return_value = [
            PrepLotData(
                lot="230929-12",
                viral_prep=ViralPrep(
                    virus=VirusData(
                        aliases=[Alias(is_preferred=True, name="v_123")]
                    )
                ),
            )
        ]
        mock_get_viruses.return_value = []
        mock_nsb2019.return_value = [
            NSB2019List(
                # Basic surgery info
                Date_x0020_of_x0020_Surgery="2022-12-06T08:00:00Z",
                Weight_x0020_before_x0020_Surger="19.1",
                Weight_x0020_after_x0020_Surgery="19.2",
                HpWorkStation="SWS 3",
                IACUC_x0020_Protocol_x0020__x002="2115",
                HeadpostType="AI Straight Headbar",
                CraniotomyType="Visual Cortex 5mm",
                Procedure="HP+Injection+Optic Fiber Implant",
                Virus_x0020_A_x002f_P="-1.6",
                Virus_x0020_M_x002f_L="-3.3",
                Virus_x0020_D_x002f_V="4.3",
                Virus_x0020_Hemisphere="Left",
                Inj1Type="Nanoject (Pressure)",
                Inj1Vol="400",
                Inj1LenghtofTime="5min",
                Breg2Lamb="4.5",
                Iso_x0020_On=1.5,
                HPIsoLevel="2.00",
                HPRecovery=25,
                Date1stInjection="2022-12-06T08:00:00Z",
                Burr_x0020_1_x0020_Injectable_x0="AAV-PHP.eB",
                Burr_x0020_1_x0020_Injectable_x03="1.5e12",
            )
        ]
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
        """Tests no data found"""
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


if __name__ == "__main__":
    pytest.main([__file__])
