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
        # TODO: find out how subject_id is tracked in Task_Set
        return (
            "SELECT"
            f"    TS.ID AS {TaskSetQueryColumns.TASK_ID.value},"
            f"    TS.TASK_TYPE_ID AS {TaskSetQueryColumns.TASK_TYPE_ID.value},"
            f"    TS.START_DATE AS {TaskSetQueryColumns.DATE_START.value},"
            f"    TS.END_DATE AS {TaskSetQueryColumns.DATE_END.value},"
            f"    TS.EXPERIMENTER AS {TaskSetQueryColumns.INVESTIGATOR_ID.value},"
            f"    TASK_SET_OBJECT.TASK_OBJECT AS {TaskSetQueryColumns.TASK_OBJECT.value},"
            "  FROM TASK_SET TS"
            "    LEFT OUTER JOIN TASK_SET TASK_SET_OBJECT"
            "    ON TS.ID = TASK_SET_OBJECT.TASK_ID"
            f" WHERE TS.TASK_NAME LIKE %{subject_id}%"
            f" OR TS. TASK_NUMBER LIKE %{subject_id}%;"
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
