"""Tests mapping for subject module"""

import unittest
from datetime import date, datetime

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
from aind_labtracks_service_async_client import MouseCustomClass
from aind_labtracks_service_async_client.models.subject import (
    Subject as LabtrackSubject,
)
from aind_mgi_service_async_client import MgiSummaryRow

from aind_metadata_service_server.mappers.subject import SubjectMapper


class TestSubjectMapper(unittest.TestCase):
    """Test methods in SubjectMapper class"""

    def test_map_allele_info_to_pid_name(self):
        """Tests _map_allele_info_to_pid_name method"""
        allele_info = MgiSummaryRow(
            detail_uri="/allele/MGI:3590684",
            feature_type="Targeted allele",
            strand="-",
            chromosome="15",
            stars="****",
            best_match_text="Parvalbumin-IRES-Cre",
            best_match_type="Synonym",
            name="parvalbumin; targeted mutation 1, Silvia Arber",
            location="78075314-78090600",
            symbol="Pvalb<tm1(cre)Arbr>",
        )
        pid_name = SubjectMapper._map_allele_info_to_pid_name(allele_info)
        expected_pid_name = PIDName(
            name="Pvalb<tm1(cre)Arbr>",
            abbreviation=None,
            registry=Registry.MGI,
            registry_identifier="3590684",
        )
        self.assertEqual(expected_pid_name, pid_name)
        self.assertIsNone(
            SubjectMapper._map_allele_info_to_pid_name(MgiSummaryRow())
        )

    def test_map_genotype_method(self):
        """Tests _map_genotype method"""
        subject = LabtrackSubject(
            id="123",
            class_values=MouseCustomClass(
                full_genotype=(
                    "Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt"
                )
            ),
        )
        subject_missing_info = LabtrackSubject(id="123")
        self.assertEqual(
            "Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
            SubjectMapper(labtracks_subject=subject)._map_genotype(),
        )
        self.assertIsNone(
            SubjectMapper(
                labtracks_subject=subject_missing_info
            )._map_genotype()
        )

    def test_get_allele_names_from_genotype(self):
        """Tests get_allele_names_from_genotype method"""
        subject = LabtrackSubject(
            id="123",
            class_values=MouseCustomClass(
                full_genotype=(
                    "Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt"
                )
            ),
        )
        subject_missing_info = LabtrackSubject(id="123")
        self.assertEqual(
            ["Pvalb-IRES-Cre", "RCL-somBiPoles_mCerulean-WPRE"],
            SubjectMapper(
                labtracks_subject=subject
            ).get_allele_names_from_genotype(),
        )
        self.assertEqual(
            [],
            SubjectMapper(
                labtracks_subject=subject_missing_info
            ).get_allele_names_from_genotype(),
        )

    def test_map_sex(self):
        """Tests _map_sex method"""

        self.assertEqual(Sex.MALE, SubjectMapper._map_sex("m"))
        self.assertEqual(Sex.FEMALE, SubjectMapper._map_sex("f"))
        self.assertIsNone(SubjectMapper._map_sex(None))

    def test_map_to_background_strain(self):
        """Tests _map_to_background_strain method."""

        self.assertEqual(
            BackgroundStrain.BALB_c,
            SubjectMapper._map_to_background_strain("BALB/c"),
        )
        self.assertEqual(
            BackgroundStrain.C57BL_6J,
            SubjectMapper._map_to_background_strain("C57BL/6J"),
        )
        self.assertIsNone(SubjectMapper._map_to_background_strain(None))

    def test_map_species(self):
        """Tests _map_species method."""

        self.assertEqual(
            Species.MUS_MUSCULUS, SubjectMapper._map_species("mouse")
        )
        self.assertIsNone(SubjectMapper._map_species(None))

    def test_map_housing(self):
        """Tests _map_housing method."""

        self.assertEqual(
            Housing(room_id="1", cage_id=None),
            SubjectMapper._map_housing(room_id=str(1), cage_id=str(-99999)),
        )
        self.assertIsNone(
            SubjectMapper._map_housing(cage_id=None, room_id=None)
        )

    def test_map_breeding_info(self):
        """Tests _map_breeding_info method."""
        subject_complete_info = LabtrackSubject(
            id="123",
            group_name="A",
            paternal_id="B",
            maternal_id="D",
            paternal_class_values=MouseCustomClass(full_genotype="C"),
            maternal_class_values=MouseCustomClass(full_genotype="E"),
        )
        subject_incomplete_info = LabtrackSubject(
            id="123",
            group_name="A",
        )
        subject_no_info = LabtrackSubject(
            id="123",
        )
        self.assertEqual(
            BreedingInfo(
                breeding_group="A",
                paternal_id="B",
                paternal_genotype="C",
                maternal_id="D",
                maternal_genotype="E",
            ),
            SubjectMapper(subject_complete_info)._map_breeding_info(),
        )
        self.assertEqual(
            BreedingInfo.model_construct(
                breeding_group="A",
                maternal_id=None,
                maternal_genotype=None,
                paternal_id=None,
                paternal_genotype=None,
            ),
            SubjectMapper(subject_incomplete_info)._map_breeding_info(),
        )
        self.assertIsNone(SubjectMapper(subject_no_info)._map_breeding_info())

    def test_map_to_aind_subject(self):
        """Tests _map_to_aind_subject method."""
        subject = LabtrackSubject(
            id="632269",
            class_values=MouseCustomClass(
                reserved_by="Person A",
                reserved_date="2022-07-14T00:00:00-07:00",
                reason=None,
                solution="1xPBS",
                full_genotype=(
                    "Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt"
                ),
                phenotype=(
                    "P19: TSTW. Small body, large head, slightly dehydrated. "
                    "3.78g. P22: 5.59g. P26: 8.18g. Normal body proportions. "
                ),
            ),
            sex="F",
            birth_date=datetime(2022, 5, 1, 0, 0),
            species_name="mouse",
            cage_id="-99999999999999",
            room_id="-99999999999999.0000000000",
            paternal_id="623236",
            paternal_class_values=MouseCustomClass(
                reserved_by="Person One ",
                reserved_date="2022-11-01T00:00:00",
                reason="eu-retire",
                solution=None,
                full_genotype="RCL-somBiPoles_mCerulean-WPRE/wt",
                phenotype="P87: F.G. P133: Barberer. ",
            ),
            maternal_id="615310",
            maternal_class_values=MouseCustomClass(
                reserved_by="Person One ",
                reserved_date="2022-08-03T00:00:00",
                reason="Eu-retire",
                solution=None,
                full_genotype="Pvalb-IRES-Cre/wt",
                phenotype="P100: F.G.",
            ),
            group_name="Exp-ND-01-001-2109",
            group_description="BALB/c",
        )
        mapper = SubjectMapper(subject)
        aind_subject = mapper.map_to_aind_subject()
        expected_subject = Subject(
            describedBy=(
                "https://raw.githubusercontent.com/AllenNeuralDynamics/"
                "aind-data-schema/main/src/aind_data_schema/core/subject.py"
            ),
            schema_version="1.0.3",
            subject_id="632269",
            sex="Female",
            date_of_birth=date(2022, 5, 1),
            genotype="Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
            species=Species.MUS_MUSCULUS,
            background_strain="BALB/c",
            breeding_info=BreedingInfo(
                breeding_group="Exp-ND-01-001-2109",
                maternal_id="615310",
                maternal_genotype="Pvalb-IRES-Cre/wt",
                paternal_id="623236",
                paternal_genotype="RCL-somBiPoles_mCerulean-WPRE/wt",
            ),
            source=Organization.AI,
        )
        self.assertEqual(expected_subject, aind_subject)

    def test_map_to_aind_invalid_subject(self):
        """Tests _map_to_aind_subject method when there is incomplete info."""
        subject = LabtrackSubject(
            id="123",
        )
        mapper = SubjectMapper(subject)
        aind_subject = mapper.map_to_aind_subject()
        expected_subject = Subject.model_construct(
            subject_id="123",
            source=Organization.OTHER,
            species=None,
            sex=None,
            date_of_birth=None,
        )
        self.assertEqual(expected_subject, aind_subject)


if __name__ == "__main__":
    unittest.main()
