"""Tests mapping for rig_and_instrument module"""

import unittest
from datetime import date
from decimal import Decimal

from aind_data_schema.components.devices import Tube
from aind_data_schema.core.instrument import ImagingInstrumentType, Instrument
from aind_data_schema.core.rig import Rig
from aind_data_schema_models.modalities import Modality
from aind_data_schema_models.organizations import Organization

from aind_metadata_service_server.mappers.rig_and_instrument import (
    RigAndInstrumentMapper,
)


class TestRigAndInstrumentMapper(unittest.TestCase):
    """Test methods in RigAndInstrumentMapper class"""

    def test_map_to_rig(self):
        """Tests map_to_rig method"""

        slims_data1 = Rig(
            rig_id="abc_123_20201010",
            modification_date=date(2025, 1, 1),
            mouse_platform=Tube(name="tube", diameter=Decimal("10.0")),
            modalities=[Modality.CONFOCAL],
            calibrations=[],
        ).model_dump(mode="json", exclude_none=True)
        slims_data2 = {"rig_id": "abc_123_20201011"}
        mapper = RigAndInstrumentMapper(
            slims_models=[slims_data1, slims_data2]
        )
        rigs = mapper.map_to_rigs()
        expected_rigs = [
            Rig(**slims_data1),
            Rig.model_construct(**slims_data2),
        ]
        self.assertEqual(expected_rigs, rigs)

    def test_map_to_instrument(self):
        """Tests map_to_instrument method"""

        slims_data1 = Instrument(
            instrument_id="abc_123_20201010",
            modification_date=date(2025, 1, 1),
            instrument_type=ImagingInstrumentType.CONFOCAL,
            manufacturer=Organization.AIND,
            objectives=[],
        ).model_dump(mode="json", exclude_none=True)
        slims_data2 = dict()
        mapper = RigAndInstrumentMapper(
            slims_models=[slims_data1, slims_data2]
        )
        instruments = mapper.map_to_instruments()
        expected_instruments = [
            Instrument(**slims_data1),
            Instrument.model_construct(**slims_data2),
        ]
        self.assertEqual(expected_instruments, instruments)


if __name__ == "__main__":
    unittest.main()
