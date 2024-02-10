"""Module to test LabTracksResponseHandler methods."""

import unittest
from datetime import date, datetime
from decimal import Decimal

from aind_data_schema.core.procedures import (
    Perfusion,
    Procedures,
    RetroOrbitalInjection,
    Surgery,
)
from aind_data_schema.core.subject import (
    BackgroundStrain,
    BreedingInfo,
    Housing,
    Sex,
    Species,
    Subject,
)
from aind_data_schema.models.organizations import Organization

from aind_metadata_service.labtracks.client import (
    LabTracksBgStrain,
    LabTracksResponseHandler,
    LabTracksSex,
    LabTracksSpecies,
)


class TestResponseExamples:
    """Class to hold some examples"""

    class_values_str = (
        '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema">\r\n '
        "<Reserved_by>Jane Doe</Reserved_by>\r\n "
        "<Reserve_Date>2013-07-10T00:00:00-07:00</Reserve_Date>\r\n "
        "<Reason>Maintenance Breeding</Reason>\r\n "
        "<Full_Genotype>Adora2a-Cre/wt</Full_Genotype>\r\n</MouseCustomClass> "
    )
    paternal_class_values_str = (
        '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema">\r\n '
        "<Reserved_by>Jane Doe</Reserved_by>\r\n "
        "<Reserve_Date>2013-01-30T00:00:00-08:00</Reserve_Date>\r\n "
        "<Reason>Breeder Refresh</Reason>\r\n "
        "<Full_Genotype>Adora2a-Cre/wt</Full_Genotype>\r\n</MouseCustomClass>"
    )
    maternal_class_values_str = (
        '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema">\r\n '
        "<Reserved_by>Jane Doe</Reserved_by>\r\n "
        "<Reserve_Date>2013-01-30T00:00:00-08:00</Reserve_Date>\r\n "
        "<Reason>Breeder Refresh</Reason>\r\n "
        "<Full_Genotype>wt/wt</Full_Genotype>\r\n</MouseCustomClass> "
    )
    test_subject_response = [
        {
            "id": Decimal("115977"),
            "class_values": class_values_str,
            "sex": "M",
            "birth_date": datetime(2012, 5, 13, 0, 0),
            "mouse_comment": None,
            "paternal_id": Decimal("107384"),
            "paternal_class_values": paternal_class_values_str,
            "maternal_id": Decimal("107392"),
            "maternal_class_values": maternal_class_values_str,
            "species_name": "mouse",
            "group_name": "C57BL6J_OLD",
            "group_description": "C57BL/6J",
            "cage_id": "1234",
            "room_id": "000",
        }
    ]

    expected_housing = Housing(room_id="000", cage_id="1234")

    expected_subject = Subject(
        species=Species.MUS_MUSCULUS,
        breeding_info=BreedingInfo(
            breeding_group="C57BL6J_OLD",
            maternal_id="107392",
            maternal_genotype="wt/wt",
            paternal_id="107384",
            paternal_genotype="Adora2a-Cre/wt",
        ),
        subject_id="115977",
        sex=Sex.MALE,
        source=Organization.AI,
        date_of_birth=date(2012, 5, 13),
        genotype="Adora2a-Cre/wt",
        alleles=[],
        background_strain=BackgroundStrain.C57BL_6J,
        housing=expected_housing,
        rrid=None,
        restrictions=None,
        wellness_reports=[],
        notes=None,
    )

    test_procedures_response = [
        {
            "id": Decimal(00000),
            "task_type_id": Decimal(12345),
            "type_name": "Perfusion Gel",
            "date_start": datetime(2022, 10, 11, 0, 0),
            "date_end": datetime(2022, 10, 11, 4, 30),
            "investigator_id": Decimal(28803),
            "task_object": Decimal(115977),
            "protocol_number": Decimal(2002),
            "task_status": "F",
        },
        {
            "id": Decimal(00000),
            "task_type_id": Decimal(12345),
            "type_name": "Perfusion Gel",
            "date_start": datetime(2022, 10, 11, 0, 0),
            "date_end": datetime(2022, 10, 11, 4, 30),
            "investigator_id": Decimal(28803),
            "task_object": Decimal(115977),
            "protocol_number": Decimal(2002),
            "task_status": "C",
        },
        {
            "id": Decimal(10000),
            "task_type_id": Decimal(23),
            "type_name": "RO Injection VGT",
            "date_start": datetime(2022, 5, 11, 0, 0),
            "date_end": datetime(2022, 5, 12, 0, 0),
            "investigator_id": Decimal(28803),
            "task_object": Decimal(115977),
            "protocol_number": Decimal(2002),
            "task_status": "F",
        },
    ]

    expected_subject_procedures = [
        Surgery.model_construct(
            start_date=date(2022, 10, 11),
            experimenter_full_name="28803",
            iacuc_protocol="2002",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=None,
            notes=None,
            # Perfusion missing protocol_id
            procedures=[
                Perfusion.model_construct(output_specimen_ids={"115977"})
            ],
        ),
        Surgery.model_construct(
            start_date=date(2022, 5, 11),
            experimenter_full_name="28803",
            iacuc_protocol="2002",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=None,
            notes=None,
            # Missing injection_volume and injection_eye
            procedures=[
                RetroOrbitalInjection.model_construct(
                    injection_volume=None, injection_eye=None
                )
            ],
        ),
    ]

    expected_procedures = Procedures.model_construct(
        subject_id="115977",
        subject_procedures=expected_subject_procedures,
    )


class TestLabTracksResponseHandler(unittest.TestCase):
    """Class for unit tests on LabTracksResponseHandler."""

    rh = LabTracksResponseHandler()

    def test_map_response_to_procedures(self):
        """Tests that the response gets mapped to the subject."""
        actual_procedures = self.rh.map_response_to_procedures(
            "115977", TestResponseExamples.test_procedures_response
        )
        self.assertEqual(
            TestResponseExamples.expected_subject_procedures,
            actual_procedures.subject_procedures,
        )

    def test_map_response_to_subject(self):
        """Tests that the response gets mapped to the subject."""
        actual_subject = self.rh.map_response_to_subject(
            TestResponseExamples.test_subject_response
        )
        self.assertEqual(
            [TestResponseExamples.expected_subject], actual_subject
        )

    def test_map_class_values_to_genotype(self):
        """Tests that the genotype is extracted from the xml string."""
        deformed_class_values_str = (
            '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  '
            "<Reserved_by>Mary Smith </Reserved_by>\r\n  "
            "<Reserve_Date>2022-06-27T00:00:00</Reserve_Date>\r\n  "
            "<Reason>EU-retire</Reason>\r\n</MouseCustomClass>"
        )

        output = self.rh._map_class_values_to_genotype(
            deformed_class_values_str
        )
        self.assertIsNone(output)
        self.assertIsNone(self.rh._map_class_values_to_genotype(None))

    def test_map_species(self):
        """Tests LabTracks species is mapped to aind_data_schema species."""
        mouse = LabTracksSpecies.MOUSE.value

        subject_species = self.rh._map_species(mouse)
        none = self.rh._map_species("RANDOM_STUFF_dasfew32512")
        self.assertEqual(subject_species, Species.MUS_MUSCULUS)
        self.assertIsNone(none)
        self.assertIsNone(self.rh._map_species(None))

    def test_map_sex(self):
        """Tests that the LabTracks sex is mapped to aind_data_schema sex."""

        male = LabTracksSex.MALE.value
        female = LabTracksSex.FEMALE.value

        subject_male = self.rh._map_sex(male)
        subject_female = self.rh._map_sex(female)
        none = self.rh._map_sex("RANDOM_STUFF_afknewalofn1241413")

        self.assertEqual(subject_male, Sex.MALE)
        self.assertEqual(subject_female, Sex.FEMALE)
        self.assertIsNone(none)
        self.assertIsNone(self.rh._map_sex(None))

    def test_map_bg_strain(self):
        """Tests that the LabTracks strain is mapped correctly"""
        strain1 = LabTracksBgStrain.BALB_C.value
        strain2 = LabTracksBgStrain.C57BL_6J.value

        subject_strain1 = self.rh._map_to_background_strain(strain1)
        subject_strain2 = self.rh._map_to_background_strain(strain2)
        none = self.rh._map_to_background_strain("RANDOM_STUFF_afknewalofn1")

        self.assertEqual(subject_strain1, BackgroundStrain.BALB_c)
        self.assertEqual(subject_strain2, BackgroundStrain.C57BL_6J)
        self.assertIsNone(none)
        self.assertIsNone(self.rh._map_to_background_strain(None))

    def test_map_housing(self):
        """Tests that the LabTracks housing info is mapped correctly"""
        housing2 = Housing.model_construct(room_id="000")
        housing3 = Housing.model_construct(cage_id="1234")
        housing4 = Housing.model_construct(room_id="000", cage_id="1234")

        subject_housing1 = self.rh._map_housing(
            room_id="-99999999999", cage_id=None
        )
        subject_housing2 = self.rh._map_housing(room_id="000", cage_id=None)
        subject_housing3 = self.rh._map_housing(room_id=None, cage_id="1234")
        subject_housing4 = self.rh._map_housing(room_id="000", cage_id="1234")

        self.assertIsNone(subject_housing1)
        self.assertEqual(subject_housing2, housing2)
        self.assertEqual(subject_housing3, housing3)
        self.assertEqual(subject_housing4, housing4)


if __name__ == "__main__":
    unittest.main()
