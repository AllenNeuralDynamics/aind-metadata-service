"""Module to test LabTracksResponseHandler methods."""
import datetime
import unittest
from decimal import Decimal

from aind_data_schema import Subject
from aind_data_schema.subject import BackgroundStrain, Sex, Species

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
    test_response = [
        {
            "id": Decimal("115977"),
            "class_values": class_values_str,
            "sex": "M",
            "birth_date": datetime.datetime(2012, 5, 13, 0, 0),
            "mouse_comment": None,
            "paternal_id": Decimal("107384"),
            "paternal_class_values": paternal_class_values_str,
            "maternal_id": Decimal("107392"),
            "maternal_class_values": maternal_class_values_str,
            "species_name": "mouse",
            "group_name": "C57BL6J_OLD",
            "group_description": "C57BL/6J",
        }
    ]

    expected_subject = Subject.parse_obj(
        {
            "schema_version": "0.3.0",
            "species": "Mus musculus",
            "subject_id": "115977",
            "sex": "Male",
            "date_of_birth": "2012-05-13",
            "genotype": "Adora2a-Cre/wt",
            "maternal_id": "107392",
            "maternal_genotype": "wt/wt",
            "paternal_id": "107384",
            "paternal_genotype": "Adora2a-Cre/wt",
            "breeding_group": "C57BL6J_OLD",
            "background_strain": "C57BL/6J",
        }
    )


class TestLabTracksResponseHandler(unittest.TestCase):
    """Class for unit tests on LabTracksResponseHandler."""

    rh = LabTracksResponseHandler()

    def test_map_response_to_subject(self):
        """Tests that the response gets mapped to the subject."""
        actual_subject = self.rh.map_response_to_subject(
            TestResponseExamples.test_response
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


if __name__ == "__main__":
    unittest.main()
