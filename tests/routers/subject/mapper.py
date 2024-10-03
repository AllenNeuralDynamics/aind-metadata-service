"""Tests mapper module"""

import unittest
from datetime import date, datetime

from aind_data_schema.core.subject import (
    Sex,
    BackgroundStrain,
    Housing,
    BreedingInfo,
    Subject,
)
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.species import Species

from aind_metadata_service.backends.labtracks.models import (
    Subject as LabTracksSubject,
    SexNames,
    SpeciesNames,
    MouseCustomClass,
    BgStrains,
)
from aind_metadata_service.routers.subject.mapper import Mapper


class TestMapper(unittest.TestCase):
    """Tests methods in Mapper class"""

    def test_map_sex(self):
        with self.assertLogs() as captured:
            lb_model1 = LabTracksSubject(id=123456, sex=SexNames.MALE)
            lb_model2 = LabTracksSubject(id=123456, sex=SexNames.FEMALE)
            lb_model3 = LabTracksSubject(id=123456, sex="unknown")
            lb_model4 = LabTracksSubject(id=123456)
            expected1 = Sex.MALE
            expected2 = Sex.FEMALE
            actual1 = Mapper(lab_tracks_subject=lb_model1)._map_sex()
            actual2 = Mapper(lab_tracks_subject=lb_model2)._map_sex()
            actual3 = Mapper(lab_tracks_subject=lb_model3)._map_sex()
            actual4 = Mapper(lab_tracks_subject=lb_model4)._map_sex()
        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2, actual2)
        self.assertIsNone(actual3)
        self.assertIsNone(actual4)
        self.assertEqual(
            ["WARNING:root:Unmatched lab_tracks_sex unknown"], captured.output
        )

    def test_map_species(self):
        with self.assertLogs() as captured:
            lb_model1 = LabTracksSubject(
                id=123456, species_name=SpeciesNames.MOUSE
            )
            lb_model2 = LabTracksSubject(
                id=123456, species_name=SpeciesNames.RAT
            )
            lb_model3 = LabTracksSubject(id=123456, species_name="unknown")
            lb_model4 = LabTracksSubject(id=123456)
            expected1 = Species.MUS_MUSCULUS
            expected2 = Species.RATTUS_NORVEGICUS
            actual1 = Mapper(lab_tracks_subject=lb_model1)._map_species()
            actual2 = Mapper(lab_tracks_subject=lb_model2)._map_species()
            actual3 = Mapper(lab_tracks_subject=lb_model3)._map_species()
            actual4 = Mapper(lab_tracks_subject=lb_model4)._map_species()
        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2, actual2)
        self.assertIsNone(actual3)
        self.assertIsNone(actual4)
        self.assertEqual(
            ["WARNING:root:Unmatched lab_tracks_species unknown"],
            captured.output,
        )

    def test_map_bg_strain(self):
        with self.assertLogs() as captured:
            lb_model1 = LabTracksSubject(
                id=123456, group_description=BgStrains.BALB_C
            )
            lb_model2 = LabTracksSubject(
                id=123456, group_description=BgStrains.C57BL_6J
            )
            lb_model3 = LabTracksSubject(
                id=123456, group_description="unknown"
            )
            lb_model4 = LabTracksSubject(id=123456)
            expected1 = BackgroundStrain.BALB_c
            expected2 = BackgroundStrain.C57BL_6J
            actual1 = Mapper(lab_tracks_subject=lb_model1)._map_bg_strain()
            actual2 = Mapper(lab_tracks_subject=lb_model2)._map_bg_strain()
            actual3 = Mapper(lab_tracks_subject=lb_model3)._map_bg_strain()
            actual4 = Mapper(lab_tracks_subject=lb_model4)._map_bg_strain()
        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2, actual2)
        self.assertIsNone(actual3)
        self.assertIsNone(actual4)
        self.assertEqual(
            ["WARNING:root:Unmatched lab_tracks_bg_strain unknown"],
            captured.output,
        )

    def test_map_housing(self):
        lb_model1 = LabTracksSubject(id=123456, room_id=-999, cage_id=1)
        lb_model2 = LabTracksSubject(id=123456, room_id=1, cage_id=2)
        lb_model3 = LabTracksSubject(id=123456, room_id=1, cage_id=-999)
        lb_model4 = LabTracksSubject(id=123456, room_id=-999, cage_id=-999)
        lb_model5 = LabTracksSubject(id=123456)
        expected1 = Housing(cage_id="1")
        expected2 = Housing(room_id="1", cage_id="2")
        expected3 = Housing(room_id="1")
        actual1 = Mapper(lab_tracks_subject=lb_model1)._map_housing()
        actual2 = Mapper(lab_tracks_subject=lb_model2)._map_housing()
        actual3 = Mapper(lab_tracks_subject=lb_model3)._map_housing()
        actual4 = Mapper(lab_tracks_subject=lb_model4)._map_housing()
        actual5 = Mapper(lab_tracks_subject=lb_model5)._map_housing()

        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2, actual2)
        self.assertEqual(expected3, actual3)
        self.assertIsNone(actual4)
        self.assertIsNone(actual5)

    def test_map_breeding_info(self):

        paternal_class_values = MouseCustomClass(
            full_genotype="RCL-somBiPoles_mCerulean-WPRE/wt"
        )
        maternal_class_values = MouseCustomClass(
            full_genotype="Pvalb-IRES-Cre/wt"
        )

        lb_model1 = LabTracksSubject(
            id=123456,
            group_name="Pvalb-IRES-Cre;RCL-somBiPoles_mCerulean-WPRE(ND)",
            maternal_class_values=maternal_class_values,
            paternal_class_values=paternal_class_values,
            maternal_id=123455,
            paternal_id=123454,
        )
        lb_model2 = LabTracksSubject(
            id=123456,
            group_name="Pvalb-IRES-Cre;RCL-somBiPoles_mCerulean-WPRE(ND)",
            maternal_class_values=maternal_class_values,
            maternal_id=123455,
        )
        lb_model3 = LabTracksSubject(id=123456)
        expected1 = BreedingInfo(
            breeding_group="Pvalb-IRES-Cre;RCL-somBiPoles_mCerulean-WPRE(ND)",
            maternal_id="123455",
            maternal_genotype="Pvalb-IRES-Cre/wt",
            paternal_id="123454",
            paternal_genotype="RCL-somBiPoles_mCerulean-WPRE/wt",
        )
        expected2 = BreedingInfo.model_construct(
            breeding_group="Pvalb-IRES-Cre;RCL-somBiPoles_mCerulean-WPRE(ND)",
            maternal_id="123455",
            maternal_genotype="Pvalb-IRES-Cre/wt",
            paternal_id=None,
            paternal_genotype=None,
        )
        actual1 = Mapper(lab_tracks_subject=lb_model1)._map_breeding_info()
        actual2 = Mapper(lab_tracks_subject=lb_model2)._map_breeding_info()
        actual3 = Mapper(lab_tracks_subject=lb_model3)._map_breeding_info()
        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2, actual2)
        self.assertIsNone(actual3)

    def test_map_source(self):
        """Tests _map_source method"""

        breeding_info1 = BreedingInfo(
            breeding_group="Pvalb-IRES-Cre;RCL-somBiPoles_mCerulean-WPRE(ND)",
            maternal_id="123455",
            maternal_genotype="Pvalb-IRES-Cre/wt",
            paternal_id="123454",
            paternal_genotype="RCL-somBiPoles_mCerulean-WPRE/wt",
        )
        expected1 = Organization.AI
        expected2 = Organization.OTHER
        actual1 = Mapper._map_source(breeding_info1)
        actual2 = Mapper._map_source(None)
        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2, actual2)

    def test_map_subject(self):
        paternal_class_values = MouseCustomClass(
            full_genotype="RCL-somBiPoles_mCerulean-WPRE/wt"
        )
        maternal_class_values = MouseCustomClass(
            full_genotype="Pvalb-IRES-Cre/wt"
        )

        lb_model1 = LabTracksSubject(
            id=123456,
            class_values=MouseCustomClass(
                full_genotype=(
                    "Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt"
                ),
            ),
            birth_date=datetime(2022, 5, 1, 0, 0),
            group_name="Pvalb-IRES-Cre;RCL-somBiPoles_mCerulean-WPRE(ND)",
            maternal_class_values=maternal_class_values,
            paternal_class_values=paternal_class_values,
            maternal_id=123455,
            paternal_id=123454,
            sex=SexNames.MALE,
            species_name=SpeciesNames.MOUSE,
            group_description=BgStrains.BALB_C,
            room_id=1,
            cage_id=2,
        )
        lb_model2 = LabTracksSubject(id=123456, sex=SexNames.FEMALE)
        expected1 = Subject(
            subject_id="123456",
            sex=Sex.MALE.value,
            date_of_birth=date(2022, 5, 1),
            genotype="Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
            species=Species.MUS_MUSCULUS,
            background_strain=BackgroundStrain.BALB_c,
            breeding_info=BreedingInfo(
                breeding_group=(
                    "Pvalb-IRES-Cre;RCL-somBiPoles_mCerulean-WPRE(ND)"
                ),
                maternal_id="123455",
                maternal_genotype="Pvalb-IRES-Cre/wt",
                paternal_id="123454",
                paternal_genotype="RCL-somBiPoles_mCerulean-WPRE/wt",
            ),
            source=Organization.AI,
            housing=Housing(cage_id="2", room_id="1"),
        )
        expected2 = Subject.model_construct(
            subject_id="123456",
            date_of_birth=None,
            sex=Sex.FEMALE.value,
            source=Organization.OTHER,
            genotype=None,
            species=None,
            background_strain=None,
            breeding_info=None,
            housing=None,
        )
        actual1 = Mapper(lab_tracks_subject=lb_model1).map_to_subject()
        actual2 = Mapper(lab_tracks_subject=lb_model2).map_to_subject()
        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2, actual2)


if __name__ == "__main__":
    unittest.main()
