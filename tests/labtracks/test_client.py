"""Module to test LabTracks Client methods"""

import decimal
import unittest
from unittest.mock import Mock, patch

import pyodbc
from fastapi.responses import JSONResponse

from aind_metadata_service.labtracks.client import (
    ErrorResponseHandler,
    LabTracksClient,
)


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
    def test_labtracks_client_create_session(self, mock_connect: Mock) -> None:
        """
        Tests client session method with mocked responses
        Parameters
        ----------
        mock_connect : Mock
            A mocked Connection class that can be used to override methods
            without connecting to sqlserver

        Returns
        -------
            pass

        """

        def mock_fetchall(_):
            """Mock the fetchall method in
            pyodbc.connect().cursor().fetchall()"""
            return [
                ("A", decimal.Decimal(403231)),
                ("A", decimal.Decimal(499294)),
            ]

        type(mock_connect().cursor()).description = (
            ("Animal_Status", str.__class__, None, 1, 1, 0, False),
            ("ID", decimal.Decimal.__class__, None, 14, 14, 0, False),
        )
        type(mock_connect().cursor()).fetchall = mock_fetchall

        session = self.lb_client.create_session()
        example_query = "SELECT TOP 2 ANIMAL_STATUS, ID FROM ANIMALS_COMMON;"
        response = self.lb_client.submit_query(session, example_query)
        handled_response = self.lb_client.handle_response(response)
        expected_handled_response = {"message": "Unable to parse message."}
        mock_connect.assert_called()
        self.assertEqual(expected_handled_response, handled_response)
        self.lb_client.close_session(session)

    @patch("pyodbc.connect")
    def test_labtracks_client_submit_query_error(
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

        session = self.lb_client.create_session()
        response1 = self.lb_client.submit_query(session, "SOMETHING BAD")
        expected_response = {
            "msg": f"{ErrorResponseHandler.ErrorResponses.PYODBC_ERROR.value}: " f"ProgrammingError"
        }
        mock_connect.assert_called()
        self.assertEqual(response1, expected_response)
        self.lb_client.close_session(session)


    @patch("pyodbc.connect")
    def test_id_does_not_exist(self, mock_connect: Mock) -> None:
        """
        Tests that JSONResponse error is returned to client properly
        when queried subject_id does not exist. 
        Parameters
        ----------
        mock_connect : Mock
            A mocked Connection class that can be used to override methods
            without connecting to sqlserver

        Returns
        -------
            pass
        """
        test_response = {"msg":[]}
        subject_id = decimal.Decimal('0000')
        expected_response = JSONResponse(status_code=418, 
                content={"message": f"{ErrorResponseHandler.ErrorResponses.ID_ERROR.value}: "
                f"subject {str(subject_id)} does not exist", "data": test_response})

        actual_response = self.lb_client.get_subject_from_subject_id(subject_id)
        self.assertEqual(expected_response.body,actual_response.body)
    

if __name__ == "__main__":
    unittest.main()
