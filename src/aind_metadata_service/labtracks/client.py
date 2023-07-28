"""Module to create clients to connect to databases."""
import logging
from enum import Enum
from typing import List, Optional
from xml.etree import ElementTree as ET

import pyodbc
from aind_data_schema.procedures import (
    Perfusion,
    Procedures,
    RetroOrbitalInjection,
)
from aind_data_schema.subject import BackgroundStrain, Sex, Species, Subject

from aind_metadata_service.labtracks.query_builder import (
    LabTracksQueries,
    SubjectQueryColumns,
    TaskSetQueryColumns,
)
from aind_metadata_service.response_handler import ModelResponse, StatusCodes


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
    def close_session(session: pyodbc.Connection) -> None:
        """Closes a pyodbc session connection"""
        session.close()

    def get_subject_info(self, subject_id: str) -> ModelResponse:
        """
        Method to retrieve subject from subject_id (int)
        Parameters
        ----------
        subject_id: str
        """
        try:
            query = LabTracksQueries.subject_from_subject_id(subject_id)
            session = self.create_session()
            cursor = session.cursor()
            cursor.execute(query)
            column_names = cursor.description
            columns = [column[0].lower() for column in column_names]
            fetched_rows = cursor.fetchall()
            cursor.close()
            self.close_session(session)
            results = []
            for row in fetched_rows:
                results.append(dict(zip(columns, row)))
            lth = LabTracksResponseHandler()
            subjects = lth.map_response_to_subject(results)
            return ModelResponse(
                aind_models=subjects, status_code=StatusCodes.DB_RESPONDED
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    def get_procedures_info(self, subject_id: str) -> ModelResponse:
        """
        Method to retrieve LAS procedures from subject_id (int)
        Parameters
        ----------
        subject_id: str
        """
        try:
            query = LabTracksQueries.procedures_from_subject_id(subject_id)
            session = self.create_session()
            cursor = session.cursor()
            cursor.execute(query)
            column_names = cursor.description
            columns = [column[0].lower() for column in column_names]
            fetched_rows = cursor.fetchall()
            cursor.close()
            self.close_session(session)
            results = []
            for row in fetched_rows:
                results.append(dict(zip(columns, row)))
            lth = LabTracksResponseHandler()
            procedures = lth.map_response_to_procedures(
                subject_id=subject_id, results=results
            )
            procedures = [] if procedures is None else [procedures]
            return ModelResponse(
                aind_models=procedures, status_code=StatusCodes.DB_RESPONDED
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()


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


class LabTracksBgStrain(Enum):
    """How LabTracks labels its strains"""

    # TODO: Double check this
    C57BL_6J = "C57BL/6J"
    BALB_C = "BALB/c"


class LabTracksProcedures(Enum):
    """Keywords for LabTracks procedures"""

    PERFUSION = "Perfusion"
    RO_INJECTION = "RO Injection"


class LabTracksResponseHandler:
    """This class will contain methods to handle the response from LabTracks"""

    @staticmethod
    def _map_class_values_to_genotype(
        class_values: Optional[str],
    ) -> Optional[str]:
        """
        Extracts the full genotype from the class values field.
        Parameters
        ----------
        class_values : Optional[str]
          XML string that is expected to have a Full_Genotype field.

        Returns
        -------
          The text inside the Full_Genotype field or None if the XML string
          does not contain the Full_Genotype.

        """
        if class_values is None:
            return None
        else:
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
    def _map_species(species: Optional[str]) -> Optional[Species]:
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
        if species is None:
            return None
        if species.lower() == LabTracksSpecies.MOUSE.value.lower():
            return Species.MUS_MUSCULUS
        else:
            return None

    @staticmethod
    def _map_sex(sex: Optional[str]) -> Optional[Sex]:
        """
        Maps the LabTracks Sex enum to the aind_data_schema.subject.Sex
        Parameters
        ----------
        sex : Optional[str]
          LabTracks sex name

        Returns
        -------
          An aind_data_schema.subject.Sex or None if no such mapping exists.

        """
        if sex is None:
            return None
        if sex.lower() == LabTracksSex.MALE.value.lower():
            return Sex.MALE
        elif sex.lower() == LabTracksSex.FEMALE.value.lower():
            return Sex.FEMALE
        else:
            return None

    @staticmethod
    def _map_to_background_strain(
        bg_strain: Optional[str],
    ) -> Optional[BackgroundStrain]:
        """
        Maps the LabTracks BG Strain enum to the
        aind_data_schema.subject.BackgroundStrain
        Parameters
        ----------
        bg_strain : Optional[str]

        Returns
        -------
        Optional[BackgroundStrain]
        """

        if bg_strain is None:
            return None
        if bg_strain.lower() == LabTracksBgStrain.C57BL_6J.value.lower():
            return BackgroundStrain.C57BL_6J
        elif bg_strain.lower() == LabTracksBgStrain.BALB_C.value.lower():
            return BackgroundStrain.BALB_c
        else:
            return None

    def map_response_to_subject(self, results: List[dict]) -> List[Subject]:
        """
        Maps a response from LabTracks to an aind_data_schema.Subject
        Parameters
        ----------
        results : List[dict]
          Results pulled from LabTracks. In the form of [row]

        Returns
        -------
          A List of mapped Subjects (not validated)

        """

        subjects = []

        for result in results:
            class_values = result.get(SubjectQueryColumns.CLASS_VALUES.value)
            full_genotype = self._map_class_values_to_genotype(class_values)
            sex = self._map_sex(result.get(SubjectQueryColumns.SEX.value))
            species = self._map_species(
                result.get(SubjectQueryColumns.SPECIES_NAME.value)
            )
            paternal_genotype = self._map_class_values_to_genotype(
                result.get(SubjectQueryColumns.PATERNAL_CLASS_VALUES.value)
            )
            maternal_genotype = self._map_class_values_to_genotype(
                result.get(SubjectQueryColumns.MATERNAL_CLASS_VALUES.value)
            )
            paternal_id = result.get(SubjectQueryColumns.PATERNAL_ID.value)
            paternal_id_str = str(paternal_id) if paternal_id else None
            maternal_id = result.get(SubjectQueryColumns.MATERNAL_ID.value)
            maternal_id_str = str(maternal_id) if maternal_id else None
            subject_id = result.get(SubjectQueryColumns.ID.value)
            subject_id_str = str(subject_id) if subject_id else None
            datetime_of_birth = result.get(
                SubjectQueryColumns.BIRTH_DATE.value
            )
            date_of_birth = (
                datetime_of_birth.date() if datetime_of_birth else None
            )
            breeding_group = result.get(SubjectQueryColumns.GROUP_NAME.value)
            background_strain = self._map_to_background_strain(
                result.get(SubjectQueryColumns.GROUP_DESCRIPTION.value)
            )
            subject = Subject.construct(
                subject_id=subject_id_str,
                species=species,
                paternal_genotype=paternal_genotype,
                paternal_id=paternal_id_str,
                maternal_genotype=maternal_genotype,
                maternal_id=maternal_id_str,
                sex=sex,
                date_of_birth=date_of_birth,
                genotype=full_genotype,
                breeding_group=breeding_group,
                background_strain=background_strain,
            )
            subjects.append(subject)
        return subjects

    @staticmethod
    def map_response_to_procedures(
        subject_id: str,
        results: List[dict],
    ) -> Optional[Procedures]:
        """
        Maps a response from LabTracks to an aind_data_schema.Procedure
        Parameters
        ----------
        subject_id : str
            The subject id to map the procedures to
        results : List[dict]
            Results pulled from LabTracks. In the form of [row]

        Returns
        -------
            A List of mapped Subjects (not validated)
        """

        procedures_list = []

        for result in results:
            start_date = result.get(TaskSetQueryColumns.DATE_START.value)
            if start_date:
                start_date = start_date.date()
            end_date = result.get(TaskSetQueryColumns.DATE_END.value)
            if end_date:
                end_date = end_date.date()
            experimenter_full_name = result.get(
                TaskSetQueryColumns.INVESTIGATOR_ID.value
            )
            iacuc_protocol = result.get(
                TaskSetQueryColumns.PROTOCOL_NUMBER.value
            )
            type_name = result.get(TaskSetQueryColumns.TYPE_NAME.value)
            if type_name:
                if LabTracksProcedures.PERFUSION.value in type_name:
                    output_specimen_ids = [
                        result.get(TaskSetQueryColumns.TASK_OBJECT.value)
                    ]
                    perfusion = Perfusion.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        output_specimen_ids=output_specimen_ids,
                    )
                    procedures_list.append(perfusion)

                elif LabTracksProcedures.RO_INJECTION.value in type_name:
                    # TODO: parse inj info from comments
                    ro_injection = RetroOrbitalInjection.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                    )
                    procedures_list.append(ro_injection)
        procedures = (
            None
            if len(procedures_list) == 0
            else Procedures.construct(
                subject_id=subject_id, subject_procedures=procedures_list
            )
        )
        return procedures
