"""Module to test LabTracks Client methods"""

import datetime
import decimal
import unittest
from unittest.mock import Mock, patch

import pyodbc
from aind_data_schema.subject import Sex

from aind_metadata_service.labtracks.client import LabTracksClient
from aind_metadata_service.response_handler import Responses

from .test_response_handler import TestResponseExamples


class TestLabTracksClient(unittest.TestCase):
    """Tests client methods"""

    driver = "{FreeTDS}"
    server = "0.0.0.0"
    port = "1234"
    db = "LabTracksDB"
    user = "LabTracksUser"
    password = "LabTracksPassword"
    lb_client = LabTracksClient(
        driver=driver,
        server=server,
        port=port,
        db=db,
        user=user,
        password=password,
    )

    def test_labtracks_client_connection_string(self) -> None:
        """Tests client connection string is created correctly"""
        expected_connection_string = (
            f"Driver={self.driver};"
            f"Server={self.server};"
            f"Port={self.port};"
            f"Database={self.db};"
            f"UID={self.user};"
            f"PWD={self.password};"
        )

        self.assertEqual(
            self.lb_client.connection_str, expected_connection_string
        )

    @patch("pyodbc.connect")
    def test_labtracks_client_internal_server_error(
        self, mock_connect: Mock
    ) -> None:
        """
        Tests that pyodbc errors are returned to client properly
        Parameters
        ----------
        mock_connect : Mock
            A mocked Connection class that can be used to override methods
            without connecting to sqlserver

        Returns
        -------
            pass
        """

        def mock_cursor(_):
            """Mock the pyodbc.cursor() function."""
            raise pyodbc.ProgrammingError

        type(mock_connect.return_value).cursor = mock_cursor

        response1 = self.lb_client.get_subject_info("123")
        response2 = self.lb_client.get_procedures_info("123")
        expected_response = Responses.internal_server_error_response()
        mock_connect.assert_called()
        self.assertEqual(response1.status_code, expected_response.status_code)
        self.assertEqual(response1.body, expected_response.body)
        self.assertEqual(response2.status_code, expected_response.status_code)
        self.assertEqual(response2.body, expected_response.body)

    @patch("pyodbc.connect")
    def test_id_does_not_exist(self, _) -> None:
        """
        Tests that JSONResponse error is returned to client properly
        when queried subject_id does not exist.
        Parameters
        ----------
        _ : Mock
            A mocked Connection class that can be used to override methods
            without connecting to sqlserver

        Returns
        -------
            pass
        """
        subject_id = "00000"

        subject_response = self.lb_client.get_subject_info(subject_id)
        procedure_response = self.lb_client.get_procedures_info(subject_id)
        expected_response = Responses.no_data_found_response()
        self.assertEqual(
            expected_response.status_code, subject_response.status_code
        )
        self.assertEqual(expected_response.body, subject_response.body)
        self.assertEqual(
            expected_response.status_code, procedure_response.status_code
        )
        self.assertEqual(expected_response.body, procedure_response.body)

    @patch("pyodbc.connect")
    def test_get_subject_info_success(self, mock_connect: Mock) -> None:
        """
        Tests that JSONResponse is returned to client properly
        when queried subject_id does exist.
        Parameters
        ----------
        mock_connect : Mock
            A mocked Connection class that can be used to override methods
            without connecting to sqlserver

        Returns
        -------
            pass
        """

        class MockCursor:
            """Mocked cursor object"""

            description = [
                ["id"],
                ["class_values"],
                ["sex"],
                ["birth_date"],
                ["mouse_comment"],
                ["paternal_id"],
                ["paternal_class_values"],
                ["maternal_id"],
                ["maternal_class_values"],
                ["species_name"],
                ["group_name"],
                ["group_description"],
            ]

            @staticmethod
            def execute(_):
                """Mock execute"""
                return None

            @staticmethod
            def fetchall():
                """Mock fetchall"""
                return [
                    [
                        decimal.Decimal("115977"),
                        TestResponseExamples.class_values_str,
                        "M",
                        datetime.datetime(2012, 5, 13, 0, 0),
                        None,
                        decimal.Decimal("107384"),
                        TestResponseExamples.paternal_class_values_str,
                        decimal.Decimal("107392"),
                        TestResponseExamples.maternal_class_values_str,
                        "mouse",
                        "C57BL6J_OLD",
                        "C57BL/6J",
                    ]
                ]

            @staticmethod
            def close():
                """Mock close"""
                return None

        subject_id = "115977"

        type(mock_connect.return_value).cursor = MockCursor

        actual_response = self.lb_client.get_subject_info(subject_id)
        expected_response = Responses.model_response(
            TestResponseExamples.expected_subject
        )
        self.assertEqual(
            expected_response.status_code, actual_response.status_code
        )
        self.assertEqual(expected_response.body, actual_response.body)

    @patch("pyodbc.connect")
    def test_multiple_ids_exist(self, mock_connect: Mock) -> None:
        """
        Tests that JSONResponse error is returned to client properly
        when queried subject_id returns multiple items.
        Parameters
        ----------
        mock_connect : Mock
            A mocked Connection class that can be used to override methods
            without connecting to sqlserver

        Returns
        -------
            pass
        """

        class MockCursor:
            """Mocked cursor object"""

            description = [
                ["id"],
                ["class_values"],
                ["sex"],
                ["birth_date"],
                ["mouse_comment"],
                ["paternal_id"],
                ["paternal_class_values"],
                ["maternal_id"],
                ["maternal_class_values"],
                ["species_name"],
                ["group_name"],
                ["group_description"],
            ]

            @staticmethod
            def execute(_):
                """Mock execute"""
                return None

            @staticmethod
            def fetchall():
                """Mock fetchall"""
                return [
                    [
                        decimal.Decimal("115977"),
                        TestResponseExamples.class_values_str,
                        "M",
                        datetime.datetime(2012, 5, 13, 0, 0),
                        None,
                        decimal.Decimal("107384"),
                        TestResponseExamples.paternal_class_values_str,
                        decimal.Decimal("107392"),
                        TestResponseExamples.maternal_class_values_str,
                        "mouse",
                        "C57BL6J_OLD",
                        "C57BL/6J",
                    ],
                    [
                        decimal.Decimal("115977"),
                        TestResponseExamples.class_values_str,
                        "F",
                        datetime.datetime(2012, 5, 13, 0, 0),
                        None,
                        decimal.Decimal("107384"),
                        TestResponseExamples.paternal_class_values_str,
                        decimal.Decimal("107392"),
                        TestResponseExamples.maternal_class_values_str,
                        "mouse",
                        "C57BL6J_OLD",
                        "C57BL/6J",
                    ],
                ]

            @staticmethod
            def close():
                """Mock close"""
                return None

        subject_id = "115977"

        type(mock_connect.return_value).cursor = MockCursor

        actual_response = self.lb_client.get_subject_info(subject_id)
        expected_subject2 = TestResponseExamples.expected_subject.copy()
        expected_subject2.sex = Sex.FEMALE
        expected_response = Responses.multiple_items_found_response(
            [TestResponseExamples.expected_subject, expected_subject2]
        )
        self.assertEqual(
            expected_response.status_code, actual_response.status_code
        )
        self.assertEqual(expected_response.body, actual_response.body)

    @patch("pyodbc.connect")
    def test_get_procedure_info_success(self, mock_connect: Mock) -> None:
        """
        Tests that JSONResponse is returned to client properly
        when queried subject_id does exist.
        Parameters
        ----------
        mock_connect : Mock
            A mocked Connection class that can be used to override methods
            without connecting to sqlserver

        Returns
        -------
            pass
        """

        class MockCursor:
            """Mocked cursor object"""

            description = [
                ["id"],
                ["task_type_id"],
                ["date_start"],
                ["date_end"],
                ["investigator_id"],
                ["task_object"],
                ["type_name"],
                ["protocol_number"],
            ]

            @staticmethod
            def execute(_):
                """Mock execute"""
                return None

            @staticmethod
            def fetchall():
                """Mock fetchall"""
                return [
                    [
                        decimal.Decimal("00000"),
                        decimal.Decimal("12345"),
                        datetime.datetime(2022, 10, 11, 0, 0),
                        datetime.datetime(2022, 10, 11, 4, 30),
                        decimal.Decimal("28803"),
                        decimal.Decimal("115977"),
                        "Perfusion",
                        decimal.Decimal("2002"),
                    ],
                    [
                        decimal.Decimal("10000"),
                        decimal.Decimal("23"),
                        datetime.datetime(2022, 5, 11, 0, 0),
                        datetime.datetime(2022, 5, 12, 0, 0),
                        decimal.Decimal("28803"),
                        decimal.Decimal("115977"),
                        "RO Injection",
                        decimal.Decimal("2002"),
                    ],
                ]

            @staticmethod
            def close():
                """Mock close"""
                return None

        subject_id = "115977"

        type(mock_connect.return_value).cursor = MockCursor

        actual_response = self.lb_client.get_procedures_info(subject_id)
        expected_response = Responses.model_response(
            TestResponseExamples.expected_procedures
        )
        self.assertEqual(
            expected_response.status_code, actual_response.status_code
        )
        self.assertEqual(expected_response.body, actual_response.body)


if __name__ == "__main__":
    unittest.main()
