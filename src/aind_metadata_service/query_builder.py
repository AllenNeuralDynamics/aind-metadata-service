"""Module that returns appropriate sql query strings"""


class LabTracksQueries:
    """Class to hold sql query strings for LabTracks"""

    @staticmethod
    def subject_from_specimen_id(specimen_id):
        """
        Retrieves the information to populate metadata about subjects.

        Parameters
        ----------
        specimen_id : str
            This is the id in the LabTracks ANIMALS_COMMON table

        Returns
        -------
            str
                SQL query that can be used to retrieve the data from LabTracks
                sqlserver db.

        """
        return (
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
            f"  WHERE AC.ID={specimen_id};"
        )
