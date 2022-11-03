"""Module that returns appropriate sql query strings"""
from aind_data_schema.subject import Subject, Species, Sex
import xml.etree.ElementTree as ET
from typing import Optional


class LabTracksQueries:
    """Class to hold sql query strings for LabTracks"""

    @staticmethod
    def subject_from_specimen_id(specimen_id: str) -> str:
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


class LabTracksResponseHandler:

    @staticmethod
    def _map_class_values_to_genotype(class_values: str) -> str:
        xml_root = ET.fromstring(class_values)
        full_genotype = xml_root.find('Full_Genotype')
        if full_genotype is not None:
            full_genotype_text = full_genotype.text
            return full_genotype_text

    @staticmethod
    def _map_species(species: str) -> Optional[Species]:
        if species.lower() == 'mouse':
            return Species.MUS_MUSCULUS
        else:
            return None

    @staticmethod
    def _map_sex(sex: str) -> Optional[Sex]:
        if sex.lower() == 'm':
            return Sex.MALE
        elif sex.lower() == 'f':
            return Sex.FEMALE
        else:
            return None

    def map_response_to_subject(self, response):
        contents = response['msg'][0]
        class_values = contents['class_values']
        full_genotype = self._map_class_values_to_genotype(class_values)
        sex = self._map_sex(contents['sex'])
        species = self._map_species(contents['species_name'])
        paternal_genotype = self._map_class_values_to_genotype(contents['paternal_class_values'])
        maternal_genotype = self._map_class_values_to_genotype(contents['maternal_class_values'])
        paternal_id = contents['paternal_id']
        maternal_id = contents['maternal_id']
        subject_json = ({'subject_id': contents['id'],
                         'species': species,
                         'paternal_genotype': paternal_genotype,
                         'paternal_id': paternal_id,
                         'maternal_genotype': maternal_genotype,
                         'maternal_id': maternal_id,
                         'sex': sex,
                         'date_of_birth': contents['birth_date'],
                         'genotype': full_genotype
                         })

        subject = Subject.parse_obj(subject_json).json(exclude_none=True)

        return subject

