"""Module to create clients to connect to databases."""
from enum import Enum
from typing import Optional
from xml.etree import ElementTree as ET

from fastapi.responses import JSONResponse

import pyodbc
from aind_data_schema import Subject
from aind_data_schema.subject import Sex, Species

from aind_metadata_service.labtracks.query_builder import SubjectQueryColumns
from aind_metadata_service.labtracks.query_builder import LabTracksQueries

class ErrorResponseHandler:

    class ErrorResponses(Enum):
        """Enum of Error messages. TODO: Better way to do this?"""

        PYODBC_ERROR = "Error connecting to LabTracks Server"
        ID_ERROR = "Error finding subject"
        VALIDATION_ERROR = "Subject id missing required fields"


class LabTracksClient:
    """This class contains the api to connect to LabTracks db."""

    def __init__(
        self,
        driver: str,
        server: str,
        port: str,
        db: str,
        user: str,
        password: str,
    ) -> None:
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
    def submit_query(session: pyodbc.Connection, query: str) -> dict:
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
                "msg": f"{ErrorResponseHandler.ErrorResponses.PYODBC_ERROR.value}: "
                f"{ex.__class__.__name__}"
            }

    @staticmethod
    def close_session(session: pyodbc.Connection) -> None:
        """Closes a pyodbc session connection"""
        session.close()

    @staticmethod
    def handle_response(response: dict) -> dict:
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
        lth = LabTracksResponseHandler()
        handled_response = lth.map_response_to_subject(response)
        # TODO: Better handling here or rely on requester to handle responses?
        return handled_response
    
    def get_subject_from_subject_id(self, subject_id):
        """
        Method to retrieve subject from subject_id (int)
        Parameters
        ----------
        lb_client : LabTracksClient
        subject_id: int
        """
        query = LabTracksQueries.subject_from_subject_id(subject_id)
        session = self.create_session()
        lb_response = self.submit_query(session, query)
        self.close_session(session)
        
        if len(lb_response) == 1: 
            return JSONResponse(status_code=418, 
                content={"message": f"{ErrorResponseHandler.ErrorResponses.ID_ERROR.value}: "
                f"subject {subject_id} does not exist", "data":lb_response})
        
        return self.handle_response(lb_response)

class MouseCustomClassFields(Enum):
    """
    LabTracks stores an XML string in the class_values field. We can extract
    the full genotype of the mouse from that field.
    """

    RESERVED_BY = "Reserved_by"
    RESERVED_DATE = "Reserve_Date"
    REASON = "Reason"
    FULL_GENOTYPE = "Full_Genotype"


class LabTracksSex(Enum):
    """How LabTracks labels the sex of the species."""

    MALE = "M"
    FEMALE = "F"


class LabTracksSpecies(Enum):
    """How LabTracks stores the name of the species."""

    MOUSE = "mouse"
    RAT = "rat"


class LabTracksResponseHandler:
    """This class will contain methods to handle the response from LabTracks"""

    @staticmethod
    def _map_class_values_to_genotype(class_values: str) -> Optional[str]:
        """
        Extracts the full genotype from the class values field.
        Parameters
        ----------
        class_values : str
          XML string that is expected to have a Full_Genotype field.

        Returns
        -------
          The text inside the Full_Genotype field or None if the XML string
          does not contain the Full_Genotype.

        """
        xml_root = ET.fromstring(class_values)
        full_genotype = xml_root.find(
            MouseCustomClassFields.FULL_GENOTYPE.value
        )
        if full_genotype is not None:
            full_genotype_text = full_genotype.text
            return full_genotype_text
        else:
            return None

    @staticmethod
    def _map_species(species: str) -> Optional[Species]:
        """
        Maps the LabTracks species to the aind_data_schema.subject.Species
        Parameters
        ----------
        species : str
          LabTracks species name

        Returns
        -------
          An aind_data_schema.subject.Species or None if no mapping exists.

        """
        if species.lower() == LabTracksSpecies.MOUSE.value.lower():
            return Species.MUS_MUSCULUS
        else:
            return None

    @staticmethod
    def _map_sex(sex: str) -> Optional[Sex]:
        """
        Maps the LabTracks Sex enum to the aind_data_schema.subject.Sex
        Parameters
        ----------
        sex : str
          LabTracks sex name

        Returns
        -------
          An aind_data_schema.subject.Sex or None if no such mapping exists.

        """
        if sex.lower() == LabTracksSex.MALE.value.lower():
            return Sex.MALE
        elif sex.lower() == LabTracksSex.FEMALE.value.lower():
            return Sex.FEMALE
        else:
            return None

    def map_response_to_subject(self, response) -> dict:
        """
        Maps a response from LabTracks to an aind_data_schema.Subject json str
        Parameters
        ----------
        response : dict
          The Response is a dict like {'msg': [rows]}

        Returns
        -------
          A dict

        """
        # TODO: Handle errors
        contents = response["msg"][0]

        try:
            class_values = contents[SubjectQueryColumns.CLASS_VALUES.value]
            full_genotype = self._map_class_values_to_genotype(class_values)
            sex: Optional[Sex] = self._map_sex(
                contents[SubjectQueryColumns.SEX.value]
            )
            species = self._map_species(
                contents[SubjectQueryColumns.SPECIES_NAME.value]
            )
            paternal_genotype = self._map_class_values_to_genotype(
                contents[SubjectQueryColumns.PATERNAL_CLASS_VALUES.value]
            )
            maternal_genotype = self._map_class_values_to_genotype(
                contents[SubjectQueryColumns.MATERNAL_CLASS_VALUES.value]
            )
            paternal_id = contents[SubjectQueryColumns.PATERNAL_ID.value]
            maternal_id = contents[SubjectQueryColumns.MATERNAL_ID.value]
            subject_id = contents[SubjectQueryColumns.ID.value]
            date_of_birth = contents[SubjectQueryColumns.BIRTH_DATE.value]
            breeding_group = contents[SubjectQueryColumns.GROUP_NAME.value]
            background_strain = contents[SubjectQueryColumns.GROUP_DESCRIPTION.value]
            subject = Subject(
                subject_id=subject_id,
                species=species,
                paternal_genotype=paternal_genotype,
                paternal_id=paternal_id,
                maternal_genotype=maternal_genotype,
                maternal_id=maternal_id,
                sex=sex,
                date_of_birth=date_of_birth,
                genotype=full_genotype,
                breeding_group=breeding_group,
                background_strain=background_strain,
            )
            return {"message": subject}
        except KeyError:
            return {"message": "Unable to parse message."}
