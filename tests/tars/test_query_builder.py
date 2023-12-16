"""Module to test Tars Query Builder"""
import unittest

from aind_metadata_service.tars.query_builder import TarsQueries


class TestTarsQueries(unittest.TestCase):
    """Class to test TarsQueries methods."""

    def test_prep_lot_from_number(self):
        """Tests that query is created as expected"""
        resource = "https://some_resource.org"
        prep_lot_number = "12345"
        expected_query = (
            "https://some_resource.org/api/v1/ViralPrepLots?"
            "order=1&orderBy=id&searchFields=lot&search=12345"
        )

        result = TarsQueries.prep_lot_from_number(resource, prep_lot_number)

        self.assertEqual(result, expected_query)


if __name__ == "__main__":
    unittest.main()
