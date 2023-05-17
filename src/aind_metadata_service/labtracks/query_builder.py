"""Module that returns appropriate sql query strings"""
from enum import Enum


class SubjectQueryColumns(Enum):
    """Expected columns in the subject query response."""

    ID = "id"
    CLASS_VALUES = "class_values"
    SEX = "sex"
    BIRTH_DATE = "birth_date"
    PATERNAL_ID = "paternal_id"
    PATERNAL_CLASS_VALUES = "paternal_class_values"
    MATERNAL_ID = "maternal_id"
    MATERNAL_CLASS_VALUES = "maternal_class_values"
    SPECIES_NAME = "species_name"
    GROUP_NAME = "group_name"
    GROUP_DESCRIPTION = "group_description"


class TaskSetQueryColumns(Enum):
    """Expected columns in the task set query response."""

    TASK_ID = "id"
    TASK_TYPE_ID = "task_type_id"
    DATE_START = "date_start"
    DATE_END = "date_end"
    INVESTIGATOR_ID = "investigator_id"
    TASK_OBJECT = "task_object"
    TYPE_NAME = "type_name"
    PROTOCOL_NUMBER = "protocol_number"


class LabTracksQueries:
    """Class to hold sql query strings for LabTracks"""

    @staticmethod
    def procedures_from_subject_id(subject_id: str) -> str:
        """
        Retrieves the information to populate metadata about subjects.

        Parameters
        ----------
        subject_id : str
            This is the id in the LabTracks Task_Set table

        Returns
        -------
        str
            SQL query that can be used to retrieve the data from LabTracks
            sqlserver db.
        """
        # TODO: parsers for comments/descriptions?
        return (
            "SELECT"
            f"    TS.ID AS {TaskSetQueryColumns.TASK_ID.value},"
            f"    TS.TASK_TYPE_ID AS {TaskSetQueryColumns.TASK_TYPE_ID.value},"
            f"    TT.TYPE_NAME AS {TaskSetQueryColumns.TYPE_NAME.value},"
            f"    TS.DATE_START AS {TaskSetQueryColumns.DATE_START.value},"
            f"    TS.DATE_END AS {TaskSetQueryColumns.DATE_END.value},"
            f"    TS.INVESTIGATOR_ID AS "
            f"    {TaskSetQueryColumns.INVESTIGATOR_ID.value},"
            f"    TSO.TASK_OBJECT AS {TaskSetQueryColumns.TASK_OBJECT.value},"
            f"    AP.PROTOCOL_NUMBER AS "
            f"    {TaskSetQueryColumns.PROTOCOL_NUMBER.value}"
            "  FROM TASK_SET TS"
            "    INNER JOIN TASK_SET_OBJECT TSO "
            "    ON TS.ID = TSO.TASK_ID"
            "    INNER JOIN ANIMALS_COMMON AC "
            "    ON TSO.TASK_OBJECT = AC.ID"
            "    INNER JOIN TASK_TYPE TT "
            "    ON TS.TASK_TYPE_ID = TT.ID"
            "    INNER JOIN ACUC_PROTOCOL AP "
            "    ON TS.ACUC_LINK_ID = AP.LINK_INDEX"
            f" WHERE AC.ID={subject_id};"
        )

    @staticmethod
    def subject_from_subject_id(subject_id: str) -> str:
        """
        Retrieves the information to populate metadata about subjects.

        Parameters
        ----------
        subject_id : str
            This is the id in the LabTracks ANIMALS_COMMON table

        Returns
        -------
            str
                SQL query that can be used to retrieve the data from LabTracks
                sqlserver db.

        """
        return (
            "SELECT"
            f"    AC.ID AS {SubjectQueryColumns.ID.value},"
            f"    AC.CLASS_VALUES AS {SubjectQueryColumns.CLASS_VALUES.value},"
            f"    AC.SEX AS {SubjectQueryColumns.SEX.value},"
            f"    AC.BIRTH_DATE AS {SubjectQueryColumns.BIRTH_DATE.value},"
            f"    PATERNAL.ID AS {SubjectQueryColumns.PATERNAL_ID.value},"
            f"    PATERNAL.CLASS_VALUES "
            f"      AS {SubjectQueryColumns.PATERNAL_CLASS_VALUES.value},"
            f"    MATERNAL.ID AS {SubjectQueryColumns.MATERNAL_ID.value},"
            f"    MATERNAL.CLASS_VALUES "
            f"      AS {SubjectQueryColumns.MATERNAL_CLASS_VALUES.value},"
            f"    S.SPECIES_NAME AS {SubjectQueryColumns.SPECIES_NAME.value},"
            f"    GROUPS.GROUP_NAME AS {SubjectQueryColumns.GROUP_NAME.value},"
            f"    G.GROUP_DESCRIPTION "
            f"      AS {SubjectQueryColumns.GROUP_DESCRIPTION.value}"
            "  FROM ANIMALS_COMMON AC"
            "    LEFT OUTER JOIN ANIMALS_COMMON MATERNAL"
            "    ON AC.MATERNAL_INDEX = MATERNAL.ID"
            "    LEFT OUTER JOIN ANIMALS_COMMON PATERNAL "
            "    ON AC.PATERNAL_INDEX = PATERNAL.ID"
            "    LEFT OUTER JOIN SPECIES S "
            "    ON AC.SPECIES_ID = S.ID"
            "    LEFT OUTER JOIN GROUPS AS G "
            "    ON AC.GROUP_ID = G.ID"
            "    LEFT OUTER JOIN GROUPS "
            "    ON MATERNAL.GROUP_ID = GROUPS.ID"
            f" WHERE AC.ID={subject_id};"
        )
