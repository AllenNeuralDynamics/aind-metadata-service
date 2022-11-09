"""Module to test LabTracksResponseHandler methods."""
import datetime
import unittest
from decimal import Decimal

from aind_data_schema import Subject
from aind_data_schema.subject import Sex, Species

from aind_metadata_service.labtracks.client import (
    LabTracksResponseHandler,
    LabTracksSex,
    LabTracksSpecies,
)


class TestLabTracksResponseHandler(unittest.TestCase):
    """Class for unit tests on LabTracksResponseHandler."""

    class_values_str = (
        '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  '
        "<Reserved_by>Jane Doe</Reserved_by>\r\n  "
        "<Reserve_Date>2022-07-21T00:00:00-07:00</Reserve_Date>\r\n  "
        "<Solution>1xPBS</Solution>\r\n  "
        "<Full_Genotype>Adora2a-Cre/wt</Full_Genotype>\r\n</MouseCustomClass>"
    )
    paternal_class_values_str = (
        '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  '
        "<Reserved_by>Mary Smith </Reserved_by>\r\n  "
        "<Reserve_Date>2022-06-27T00:00:00</Reserve_Date>\r\n  "
        "<Reason>EU-retire</Reason>\r\n  "
        "<Full_Genotype>Adora2a-Cre/wt</Full_Genotype>\r\n</MouseCustomClass>"
    )
    maternal_class_values_str = (
        '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  '
        "<Reserved_by>Mary Smith </Reserved_by>\r\n  "
        "<Reserve_Date>2022-06-27T00:00:00</Reserve_Date>\r\n  "
        "<Reason>EU-retire</Reason>\r\n  "
        "<Full_Genotype>wt/wt</Full_Genotype>\r\n</MouseCustomClass>"
    )
    test_response = {
        "msg": [
            {
                "id": Decimal("625463"),
                "class_values": class_values_str,
                "sex": "M",
                "birth_date": datetime.datetime(2022, 3, 12, 0, 0),
                "mouse_comment": "PF 10/7/22",
                "paternal_id": Decimal("617425"),
                "paternal_class_values": paternal_class_values_str,
                "maternal_id": Decimal("618504"),
                "maternal_class_values": maternal_class_values_str,
                "species_name": "mouse",
                "group_name": "group_name",
            }
        ]
    }

    described_by_str = (
        "https://github.com/AllenNeuralDynamics/data_schema/blob/main/schemas/"
        "subject.py"
    )

    expected_subject = Subject.parse_obj(
        {
            "describedBy": described_by_str,
            "schema_version": "0.2.0",
            "species": "Mus musculus",
            "subject_id": "625463",
            "sex": "Male",
            "date_of_birth": "2022-03-12",
            "genotype": "Adora2a-Cre/wt",
            "maternal_id": "618504",
            "maternal_genotype": "wt/wt",
            "paternal_id": "617425",
            "paternal_genotype": "Adora2a-Cre/wt",
            "breeding_group": "group_name",
        }
    )

    rh = LabTracksResponseHandler()

    def test_map_response_to_subject(self):
        """Tests that the response gets mapped to the subject."""
        actual_subject = self.rh.map_response_to_subject(self.test_response)[
            "message"
        ]
        print("actual subject", actual_subject)
        print(self.expected_subject)
        self.assertEqual(self.expected_subject, actual_subject)

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

    def test_map_species(self):
        """Tests LabTracks species is mapped to aind_data_schema species."""
        mouse = LabTracksSpecies.MOUSE.value

        subject_species = self.rh._map_species(mouse)
        none = self.rh._map_species("RANDOM_STUFF_dasfew32512")
        self.assertEqual(subject_species, Species.MUS_MUSCULUS)
        self.assertIsNone(none)

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


if __name__ == "__main__":
    unittest.main()
