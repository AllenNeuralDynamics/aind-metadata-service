"""Maps information to aind-data-schema Subject model."""

import re
from decimal import Decimal
from typing import List, Optional

from aind_data_schema.components.subjects import (
    BreedingInfo,
    Housing,
    MouseSubject,
    Sex,
)
from aind_data_schema.core.subject import Subject
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.species import Species, Strain
from aind_labtracks_service_async_client.models.subject import (
    Subject as LabTracksSubject,
)
from aind_mgi_service_async_client.models import MgiSummaryRow
from pydantic import ValidationError

from aind_metadata_service_server.mappers.mgi_allele import MgiMapper


class SubjectMapper:
    """Class to handle mapping of data."""

    def __init__(
        self,
        labtracks_subject: LabTracksSubject,
        mgi_info: List[MgiSummaryRow] = (),
    ):
        """
        Class constructor.
        Parameters
        ----------
        labtracks_subject :  LabTracksSubject
        """
        self.labtracks_subject = labtracks_subject
        self.mgi_info = list(mgi_info)

    @staticmethod
    def _map_sex(sex: Optional[str]) -> Optional[Sex]:
        """
        Maps the LabTracks Sex enum to the aind_data_schema.subject.Sex
        Parameters
        ----------
        sex : str | None
          LabTracks sex name

        Returns
        -------
          An aind_data_schema.subject.Sex or None if no such mapping exists.

        """

        # TODO: Check if the enums can be added to the LabTracks Subject models
        match sex:
            case "m" | "M":
                return Sex.MALE
            case "f" | "F":
                return Sex.FEMALE
            case _:
                return None

    @staticmethod
    def _map_to_background_strain(
        bg_strain: Optional[str],
    ) -> Strain:
        """
        Maps the LabTracks BG Strain enum to the
        aind_data_schema.subject.BackgroundStrain
        Parameters
        ----------
        bg_strain : str | None

        Returns
        -------
        BackgroundStrain | None
        """

        match bg_strain:
            case "C57BL/6J":
                return Strain.C57BL_6J
            case "BALB/C" | "BALB/c":
                return Strain.BALB_C
            case _:
                return Strain.UNKNOWN

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
        Species | None
          An aind_data_schema.subject.Species or None if no mapping exists.

        """
        match species:
            case "mouse":
                return Species.HOUSE_MOUSE
            case _:
                return None

    @staticmethod
    def _map_housing(
        room_id: Optional[str], cage_id: Optional[str]
    ) -> Optional[Housing]:
        """
        Maps the LabTracks room_id and cage_id
        to the aind_data_schema.subject.Housing
        Parameters
        ----------
        room_id : str | None
        cage_id: str | None

        Returns
        -------
        Housing | None
        """
        room_id = (
            None
            if room_id is None or int(Decimal(room_id)) < 0
            else str(room_id)
        )
        cage_id = (
            None
            if cage_id is None or int(Decimal(cage_id)) < 0
            else str(cage_id)
        )
        if room_id or cage_id:
            return Housing(room_id=room_id, cage_id=cage_id)
        else:
            return None

    def _map_breeding_info(self) -> Optional[BreedingInfo]:
        """
        Map to BreedingInfo
        Returns
        -------
        BreedingInfo | None
        """
        labtracks_subject = self.labtracks_subject
        paternal_id = labtracks_subject.paternal_id
        if labtracks_subject.paternal_class_values:
            paternal_genotype = (
                labtracks_subject.paternal_class_values.full_genotype
            )
        else:
            paternal_genotype = None
        maternal_id = labtracks_subject.maternal_id
        if labtracks_subject.maternal_class_values:
            maternal_genotype = (
                labtracks_subject.maternal_class_values.full_genotype
            )
        else:
            maternal_genotype = None
        breeding_values = [
            paternal_id,
            paternal_genotype,
            maternal_id,
            maternal_genotype,
        ]
        # breeding_group will be deprecated in schema, so setting to empty
        if None not in breeding_values:
            return BreedingInfo(
                breeding_group="",
                paternal_id=paternal_id,
                paternal_genotype=paternal_genotype,
                maternal_id=maternal_id,
                maternal_genotype=maternal_genotype,
            )
        elif any(value is not None for value in breeding_values):
            return BreedingInfo.model_construct(
                breeding_group="",
                paternal_id=paternal_id,
                paternal_genotype=paternal_genotype,
                maternal_id=maternal_id,
                maternal_genotype=maternal_genotype,
            )
        else:
            return None

    def _map_genotype(self) -> Optional[str]:
        """Maps LabtracksSubject class values to a genotype."""
        if self.labtracks_subject.class_values:
            genotype = self.labtracks_subject.class_values.full_genotype
        else:
            genotype = None
        return genotype

    def get_allele_names_from_genotype(self) -> List[str]:
        """
        Maps a genotype to list of allele names

        Returns
        -------
        List[str]

        """
        genotype = self._map_genotype()
        if genotype is None:
            filtered_alleles = []
        else:
            alleles = re.split("[; /]", genotype)
            filtered_alleles = [a for a in alleles if a not in ["", "wt"]]
        return filtered_alleles

    def map_to_aind_subject(self) -> Subject:
        """
        Map information to aind-data-schema Subject. Will attempt to return
        a valid model. If there are any validation errors, then an invalid
        model will be returned.
        Returns
        -------
        Subject

        """
        labtracks_subject = self.labtracks_subject
        subject_id = labtracks_subject.id
        sex = self._map_sex(labtracks_subject.sex)
        bg_strain = self._map_to_background_strain(
            labtracks_subject.group_description
        )
        species = self._map_species(labtracks_subject.species_name)
        datetime_of_birth = labtracks_subject.birth_date
        date_of_birth = datetime_of_birth.date() if datetime_of_birth else None
        housing = self._map_housing(
            room_id=labtracks_subject.room_id,
            cage_id=labtracks_subject.cage_id,
        )
        genotype = self._map_genotype()
        breeding_info = self._map_breeding_info()
        if breeding_info:
            source = Organization.AI
        else:
            source = Organization.UNKNOWN
        alleles = []
        for mgi_summary_row in self.mgi_info:
            mgi_mapper = MgiMapper(mgi_summary_row=mgi_summary_row)
            pid_name = mgi_mapper.map_to_aind_pid_name()
            if pid_name is not None:
                alleles.append(pid_name)
        try:
            subject_details = MouseSubject(
                sex=sex,
                date_of_birth=date_of_birth,
                strain=bg_strain,
                species=species,
                alleles=alleles,
                genotype=genotype,
                breeding_info=breeding_info,
                housing=housing,
                source=source,
            )
            return Subject(
                subject_id=subject_id, subject_details=subject_details
            )
        except ValidationError:
            subject_details = MouseSubject.model_construct(
                sex=sex,
                date_of_birth=date_of_birth,
                strain=bg_strain,
                species=species,
                alleles=alleles,
                genotype=genotype,
                breeding_info=breeding_info,
                housing=housing,
                source=source,
            )
            return Subject.model_construct(
                subject_id=subject_id, subject_details=subject_details
            )
