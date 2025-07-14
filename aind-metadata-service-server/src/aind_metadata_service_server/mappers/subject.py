"""Maps information to aind-data-schema Subject model."""

import re
from decimal import Decimal
from typing import List, Optional

from aind_data_schema.core.subject import (
    BackgroundStrain,
    BreedingInfo,
    Housing,
    Sex,
    Subject,
)
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.registries import Registry
from aind_data_schema_models.species import Species
from aind_labtracks_service_async_client.models.subject import (
    Subject as LabTracksSubject,
)
from aind_mgi_service_async_client.models import MgiSummaryRow
from pydantic import ValidationError


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
    def _map_allele_info_to_pid_name(
        mgi_summary_row: MgiSummaryRow,
    ) -> Optional[PIDName]:
        """
        Map MgiSummaryRow to a PIDName
        Parameters
        ----------
        mgi_summary_row : MgiSummaryRow

        Returns
        -------
        Optional[PIDName]

        """

        detail_uri_pattern = re.compile(r"/allele/MGI:(\d+)")
        if mgi_summary_row.detail_uri is not None and re.match(
            detail_uri_pattern, mgi_summary_row.detail_uri
        ):
            registry_identifier = re.match(
                detail_uri_pattern, mgi_summary_row.detail_uri
            ).group(1)
        else:
            registry_identifier = None
        if (
            mgi_summary_row.stars == "****"
            and mgi_summary_row.best_match_type == "Synonym"
        ):
            return PIDName(
                name=mgi_summary_row.symbol,
                abbreviation=None,
                registry=Registry.MGI,
                registry_identifier=registry_identifier,
            )
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

        match bg_strain:
            case "C57BL/6J":
                return BackgroundStrain.C57BL_6J
            case "BALB/C" | "BALB/c":
                return BackgroundStrain.BALB_c
            case _:
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
        match species:
            case "mouse":
                return Species.MUS_MUSCULUS
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
        room_id : Optional[str]
        cage_id: Optional[str]

        Returns
        -------
        Optional[Housing]
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
        Optional[BreedingInfo]
        """
        labtracks_subject = self.labtracks_subject
        breeding_group = labtracks_subject.group_name
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
            breeding_group,
            paternal_id,
            paternal_genotype,
            maternal_id,
            maternal_genotype,
        ]
        if None not in breeding_values:
            return BreedingInfo(
                breeding_group=breeding_group,
                paternal_id=paternal_id,
                paternal_genotype=paternal_genotype,
                maternal_id=maternal_id,
                maternal_genotype=maternal_genotype,
            )
        elif any(value is not None for value in breeding_values):
            return BreedingInfo.model_construct(
                breeding_group=breeding_group,
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
        # LabTracksSubject
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
            source = Organization.OTHER
        alleles = [
            self._map_allele_info_to_pid_name(mgi_summary_row=row)
            for row in self.mgi_info
            if self._map_allele_info_to_pid_name(mgi_summary_row=row)
            is not None
        ]
        try:
            return Subject(
                subject_id=subject_id,
                date_of_birth=date_of_birth,
                sex=sex,
                species=species,
                housing=housing,
                genotype=genotype,
                background_strain=bg_strain,
                breeding_info=breeding_info,
                source=source,
                alleles=alleles,
            )
        except ValidationError:
            return Subject.model_construct(
                subject_id=subject_id,
                date_of_birth=date_of_birth,
                sex=sex,
                species=species,
                housing=housing,
                genotype=genotype,
                background_strain=bg_strain,
                breeding_info=breeding_info,
                source=source,
                alleles=alleles,
            )
