"""Tests aind_labtracks_service methods."""

import unittest

from aind_labtracks_service import query_builder


class QueryBuilderTest(unittest.TestCase):
    """Tests query_builder methods."""

    def test_subject_from_species(self):
        """Tests sql string is created correctly."""
        species_id = "625464"
        actual_output = query_builder.subject_from_species_id(species_id)
        expected_output = (
            "SELECT "
            "  AC.SEX, "
            "  AC.COMPOSITE_PEDNUM, "
            "  AC.MATERNAL_NUMBER, "
            "  AC.MATERNAL_INDEX, "
            "  AC.PATERNAL_NUMBER, "
            "  AC.PATERNAL_INDEX, "
            "  AC.BIRTH_DATE, AC.ID, "
            "  AC.MOUSE_COMMENT, "
            "  S.SPECIES_NAME "
            "FROM ANIMALS_COMMON AC "
            "  LEFT OUTER JOIN SPECIES S ON AC.SPECIES_ID = S.ID "
            f"  WHERE AC.ID={species_id};"
        )
        self.assertEqual(expected_output, actual_output)


if __name__ == "__main__":
    unittest.main()
