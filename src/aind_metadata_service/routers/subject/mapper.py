import logging
from typing import Optional

from aind_data_schema_models.species import Species
from pydantic import ValidationError

from aind_metadata_service.backends.labtracks.models import (
    Subject as LabTracksSubject,
    SexNames,
    SpeciesNames,
    BgStrains,
)
from aind_data_schema_models.organizations import Organization
from aind_data_schema.core.subject import (
    Subject,
    Sex,
    BackgroundStrain,
    BreedingInfo,
    Housing,
)


class Mapper:

    def __init__(self, lab_tracks_subject: LabTracksSubject):
        self.lab_tracks_subject = lab_tracks_subject

    def _map_sex(self) -> Optional[str]:

        lab_tracks_sex = self.lab_tracks_subject.sex

        if lab_tracks_sex is None:
            return None
        match lab_tracks_sex.upper():
            case SexNames.MALE:
                return Sex.MALE.value
            case SexNames.FEMALE:
                return Sex.FEMALE.value
            case _:
                logging.warning(f"Unmatched lab_tracks_sex {lab_tracks_sex}")

    def _map_species(self) -> Optional[Species]:

        lab_tracks_species = self.lab_tracks_subject.species_name
        if lab_tracks_species is None:
            return None

        match lab_tracks_species.lower():
            case SpeciesNames.MOUSE:
                return Species.MUS_MUSCULUS
            case SpeciesNames.RAT:
                return Species.RATTUS_NORVEGICUS
            case _:
                logging.warning(
                    f"Unmatched lab_tracks_species {lab_tracks_species}"
                )
                return None

    def _map_bg_strain(self) -> Optional[str]:
        lab_tracks_bg_strain = self.lab_tracks_subject.group_description
        if lab_tracks_bg_strain is None:
            return None
        match lab_tracks_bg_strain:
            case BgStrains.BALB_C:
                return BackgroundStrain.BALB_c.value
            case BgStrains.C57BL_6J:
                return BackgroundStrain.C57BL_6J.value
            case _:
                logging.warning(
                    f"Unmatched lab_tracks_bg_strain {lab_tracks_bg_strain}"
                )
                return None

    def _map_housing(self) -> Optional[Housing]:
        room_id = self.lab_tracks_subject.room_id
        cage_id = self.lab_tracks_subject.cage_id

        room_id = None if room_id is None or int(room_id) < 0 else str(room_id)
        cage_id = None if cage_id is None or int(cage_id) < 0 else str(cage_id)
        if room_id is None and cage_id is None:
            return None
        else:
            return Housing(room_id=room_id, cage_id=cage_id)

    def _map_breeding_info(self) -> Optional[BreedingInfo]:

        breeding_group = self.lab_tracks_subject.group_name
        if self.lab_tracks_subject.paternal_class_values is None:
            paternal_id = None
            paternal_genotype = None
        else:
            paternal_genotype = (
                self.lab_tracks_subject.paternal_class_values.full_genotype
            )
            paternal_id = str(self.lab_tracks_subject.paternal_id)
        if self.lab_tracks_subject.maternal_class_values is None:
            maternal_id = None
            maternal_genotype = None
        else:
            maternal_genotype = (
                self.lab_tracks_subject.maternal_class_values.full_genotype
            )
            maternal_id = str(self.lab_tracks_subject.maternal_id)

        if any(
            val is not None
            for val in [
                breeding_group,
                paternal_genotype,
                paternal_id,
                maternal_genotype,
                maternal_id,
            ]
        ):
            try:
                return BreedingInfo(
                    breeding_group=breeding_group,
                    paternal_genotype=paternal_genotype,
                    paternal_id=paternal_id,
                    maternal_genotype=maternal_genotype,
                    maternal_id=maternal_id,
                )
            except ValidationError:
                return BreedingInfo.model_construct(
                    breeding_group=breeding_group,
                    paternal_genotype=paternal_genotype,
                    paternal_id=paternal_id,
                    maternal_genotype=maternal_genotype,
                    maternal_id=maternal_id,
                )
        else:
            return None

    @staticmethod
    def _map_source(breeding_info: Optional[BreedingInfo]) -> Organization:
        if breeding_info is None:
            return Organization.OTHER
        else:
            return Organization.AI

    def map_to_subject(self) -> Subject:

        subject_id = str(self.lab_tracks_subject.id)
        if self.lab_tracks_subject.class_values is None:
            genotype = None
        else:
            genotype = self.lab_tracks_subject.class_values.full_genotype
        if self.lab_tracks_subject.birth_date is None:
            date_of_birth = None
        else:
            date_of_birth = self.lab_tracks_subject.birth_date.date()
        breeding_info = self._map_breeding_info()
        source = self._map_source(breeding_info=breeding_info)
        species = self._map_species()
        sex = self._map_sex()
        background_strain = self._map_bg_strain()
        housing = self._map_housing()

        try:
            return Subject(
                subject_id=subject_id,
                genotype=genotype,
                breeding_info=breeding_info,
                source=source,
                species=species,
                sex=sex,
                date_of_birth=date_of_birth,
                background_strain=background_strain,
                housing=housing,
            )
        except ValidationError:
            return Subject.model_construct(
                subject_id=subject_id,
                genotype=genotype,
                breeding_info=breeding_info,
                source=source,
                species=species,
                sex=sex,
                date_of_birth=date_of_birth,
                background_strain=background_strain,
                housing=housing,
            )
