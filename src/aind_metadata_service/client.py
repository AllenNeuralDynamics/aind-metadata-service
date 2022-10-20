"""Module to create clients to connect to databases."""

from enum import Enum
from typing import Union

import pyodbc


class ErrorResponses(Enum):
    """Enum of Error messages. TODO: Better way to do this?"""

    pyodbc_error = "Error connecting to LabTracks Server."


class LabTracksClient:
    """This class contains the api to connect to LabTracks db."""

    def __init__(self,
                 driver: str,
                 server: str,
                 port: str,
                 db: str,
                 user: str,
                 password: str) -> None:
        """
        Initialize a client
        Parameters
        ----------
        driver : str
            ODBC Driver, example {FreeTDS}
        server : str
           Server DNS or IP
        port : int
           Server port
        db : str
           LabTracks Database name to connect to
        user : str
            LabTracks user
        password : str
            Password for LabTracks user
        """
        self.driver = driver
        self.server = server
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.connection_str = (
            f"Driver={driver};"
            f"Server={server};"
            f"Port={port};"
            f"Database={db};"
            f"UID={user};"
            f"PWD={password};"
        )

    def create_session(self) -> pyodbc.Connection:
        """Use pyodbc to create a connection to sqlserver"""

        return pyodbc.connect(self.connection_str)

    @staticmethod
    def submit_query(session: pyodbc.Connection,
                     query: str) -> dict:
        """
        Submit a query using session connection.

        Parameters
        ----------
        session : A pyodbc connection
        query :  str
            The sql query to submit to LabTracks sqlserver

        Returns
        -------
            dict
                Returns a {msg: [row]} or {msg: Error String} object

        """
        try:
            cursor = session.cursor()
            cursor.execute(query)
            column_names = cursor.description
            columns = [column[0].lower() for column in column_names]
            results = []
            fetched_rows = cursor.fetchall()
            cursor.close()
            for row in fetched_rows:
                results.append(dict(zip(columns, row)))
            return {"msg": results}
        except pyodbc.Error as ex:
            # TODO: Handle errors more gracefully?
            return {
                "msg": f"{ErrorResponses.pyodbc_error.value}: "
                f"{ex.__class__.__name__}"
            }

    @staticmethod
    def close_session(session: pyodbc.Connection) -> None:
        """Closes a pyodbc session connection"""
        session.close()

    @staticmethod
    def handle_response(response: dict) -> Union[list, str]:
        """
        Handles the response received from the sqlserver
        Parameters
        ----------
        response : dict
            Something like {msg: [row]} or {msg: Error String}

        Returns
        -------
            json or error msg

        """
        msg = response["msg"]
        # TODO: Better handling here or rely on requester to handle responses?
        return msg
