"""Module to test SharePoint Client methods"""

import datetime
import json
import os
import unittest
from pathlib import Path

from aind_data_schema.procedures import (
    Anaesthetic,
    CoordinateReferenceLocation,
    Craniotomy,
    CraniotomyType,
    FiberImplant,
    Headframe,
    InjectionMaterial,
    IontophoresisInjection,
    NanojectInjection,
    OphysProbe,
    Procedures,
    Side,
    SubjectProcedure,
)
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.listitems.listitem import ListItem

from aind_metadata_service.response_handler import Responses
from aind_metadata_service.sharepoint.client import (
    ListVersions,
    SharePointClient,
)


class Examples:
    """Class to hold some examples to compare against"""

    TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
    RESOURCES_DIR = TEST_DIR / "resources"

    # 2019 list items
    # TODO: clean up json loading
    list_item1_filepath = RESOURCES_DIR / "list_item1.json"

    with open(list_item1_filepath) as f:
        list_item1_json = json.load(f)

    list_item2_filepath = RESOURCES_DIR / "list_item2.json"

    with open(list_item2_filepath) as f:
        list_item2_json = json.load(f)

    list_item3_filepath = RESOURCES_DIR / "list_item3.json"

    with open(list_item3_filepath) as f:
        list_item3_json = json.load(f)

    list_item4_filepath = RESOURCES_DIR / "list_item4.json"

    with open(list_item4_filepath) as f:
        list_item4_json = json.load(f)

    list_item5_filepath = RESOURCES_DIR / "list_item5.json"

    with open(list_item5_filepath) as f:
        list_item5_json = json.load(f)

    list_item6_filepath = RESOURCES_DIR / "list_item6.json"

    with open(list_item6_filepath) as f:
        list_item6_json = json.load(f)

    list_item7_filepath = RESOURCES_DIR / "list_item7.json"

    with open(list_item7_filepath) as f:
        list_item7_json = json.load(f)

    list_item12_filepath = RESOURCES_DIR / "list_item12.json"

    with open(list_item12_filepath) as f:
        list_item12_json = json.load(f)

    # 2023 list items
    list_item8_filepath = RESOURCES_DIR / "list_item8.json"

    with open(list_item8_filepath) as f:
        list_item8_json = json.load(f)

    list_item9_filepath = RESOURCES_DIR / "list_item9.json"

    with open(list_item9_filepath) as f:
        list_item9_json = json.load(f)

    list_item10_filepath = RESOURCES_DIR / "list_item10.json"

    with open(list_item10_filepath) as f:
        list_item10_json = json.load(f)

    list_item11_filepath = RESOURCES_DIR / "list_item11.json"

    with open(list_item11_filepath) as f:
        list_item11_json = json.load(f)

    list_item13_filepath = RESOURCES_DIR / "list_item13.json"

    with open(list_item13_filepath) as f:
        list_item13_json = json.load(f)

    list_item14_filepath = RESOURCES_DIR / "list_item14.json"

    with open(list_item14_filepath) as f:
        list_item14_json = json.load(f)

    list_item15_filepath = RESOURCES_DIR / "list_item15.json"

    with open(list_item15_filepath) as f:
        list_item15_json = json.load(f)

    list_item16_filepath = RESOURCES_DIR / "list_item16.json"

    with open(list_item16_filepath) as f:
        list_item16_json = json.load(f)

    list_item17_filepath = RESOURCES_DIR / "list_item17.json"

    with open(list_item17_filepath) as f:
        list_item17_json = json.load(f)

    described_by = (
        "https://raw.githubusercontent.com/AllenNeuralDynamics/"
        "aind-data-schema/main/src/aind_data_schema/procedures.py"
    )

    expected_inj_anaesthetic = Anaesthetic.construct(
        type="isoflurane",
        duration=None,
        level="Select...",
    )

    expected_hp_anaesthetic = Anaesthetic.construct(
        type="isoflurane",
        level="Select...",
    )

    bregma_reference = CoordinateReferenceLocation.BREGMA
    lambda_reference = CoordinateReferenceLocation.LAMBDA

    expected_probe1 = OphysProbe.construct(
        name="Probe A",
        stereotactic_coordinate_ml=-3.3,
        stereotactic_coordinate_ap=-1.6,
        stereotactic_coordinate_dv=4.2,
        angle=0.0,
        stereotactic_coordinate_reference=bregma_reference,
        bregma_to_lambda_distance=4.0,
    )

    expected_probe2 = OphysProbe.construct(
        name="Probe B",
        stereotactic_coordinate_ml=-0.6,
        stereotactic_coordinate_ap=-3.05,
        stereotactic_coordinate_dv=4.2,
        angle=0.0,
        bregma_to_lambda_distance=4.0,
        stereotactic_coordinate_reference=bregma_reference,
    )

    expected_inj_materials_1 = InjectionMaterial.construct(
        full_genome_name="Premixied &quot;\u200bdL+Cre&quot;"
    )
    expected_inj_materials_2 = InjectionMaterial.construct(
        full_genome_name="DIO-ChrimsonR"
    )

    expected_subject_procedures1 = [
        # from list item 1
        NanojectInjection.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=19.1,
            animal_weight_post=19.2,
            anaesthesia=expected_inj_anaesthetic,
            notes=None,
            injection_duration=5,
            recovery_time=None,
            workstation_id="SWS 3",
            instrument_id="Select...",
            injection_hemisphere=Side.LEFT,
            injection_coordinate_ml=-3.3,
            injection_coordinate_ap=-1.6,
            injection_coordinate_depth=4.3,
            injection_angle=0.0,
            injection_type="Nanoject (Pressure)",
            injection_volume=400.0,
            injection_materials=expected_inj_materials_1,
            injection_coordinate_reference=bregma_reference,
            bregma_to_lambda_distance=4.0,
        ),
        IontophoresisInjection.construct(
            start_date=None,
            end_date=None,
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=19.6,
            animal_weight_post=19.6,
            anaesthesia=expected_inj_anaesthetic,
            notes=None,
            injection_materials=expected_inj_materials_2,
            injection_duration=4.0,
            recovery_time=None,
            workstation_id=None,
            instrument_id="Select...",
            injection_hemisphere=Side.LEFT,
            injection_coordinate_ml=-0.6,
            injection_coordinate_ap=-3.05,
            injection_coordinate_depth=4.3,
            injection_angle=None,
            injection_type="Iontophoresis",
            injection_current=None,
            alternating_current="7/7",
            bregma_to_lambda_distance=4.0,
            injection_coordinate_reference=bregma_reference,
        ),
        Headframe.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
            anaesthesia=expected_hp_anaesthetic,
            headframe_type="AI Straight Headbar",
            headframe_part_number=None,
            well_part_number=None,
            well_type=None,
        ),
        Craniotomy.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=expected_hp_anaesthetic,
            craniotomy_type=CraniotomyType.VISCTX,
            craniotomy_hemisphere="Right",
            craniotomy_coordinates_ml=2.8,
            craniotomy_coordinates_ap=1.3,
            craniotomy_size=5.0,
            dura_removed=True,
            workstation_id="SWS 3",
            notes=None,
            bregma_to_lambda_distance=4.0,
            craniotomy_coordinates_reference=lambda_reference,
        ),
        FiberImplant.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
            probes=[expected_probe1],
        ),
        # from list item 2
        IontophoresisInjection.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=expected_inj_anaesthetic,
            notes=None,
            injection_materials=None,
            injection_duration=5,
            recovery_time=None,
            workstation_id="SWS 3",
            instrument_id="Select...",
            injection_hemisphere=Side.RIGHT,
            injection_coordinate_ml=-3.3,
            injection_coordinate_ap=-1.6,
            injection_coordinate_depth=4.3,
            injection_angle=0.0,
            injection_type="Iontophoresis",
            injection_current=5.0,
            alternating_current="7/7",
            injection_coordinate_reference=lambda_reference,
        ),
        NanojectInjection.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=expected_inj_anaesthetic,
            notes=None,
            injection_materials=None,
            injection_duration=None,
            recovery_time=None,
            workstation_id=None,
            instrument_id="NJ#4",
            injection_hemisphere=Side.RIGHT,
            injection_coordinate_ml=-0.6,
            injection_coordinate_ap=-3.05,
            injection_coordinate_depth=4.3,
            injection_angle=None,
            injection_type="Nanoject (Pressure)",
            injection_volume=400.0,
            injection_coordinate_reference=bregma_reference,
        ),
        Craniotomy.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=expected_hp_anaesthetic,
            craniotomy_type=CraniotomyType.WHC,
            craniotomy_hemisphere="Center",
            craniotomy_coordinates_ml=2.8,
            craniotomy_coordinates_ap=1.3,
            craniotomy_size=5.0,
            dura_removed=False,
            workstation_id="SWS 3",
            notes=None,
        ),
        Headframe.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
            anaesthesia=expected_hp_anaesthetic,
            headframe_type="CAM-style",
            headframe_part_number="0160-100-10 Rev A",
            well_part_number=None,
            well_type="CAM-style",
        ),
        # from list item 3
        Headframe.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
            anaesthesia=expected_hp_anaesthetic,
            headframe_type="NGC-style",
            headframe_part_number="0160-100-10",
            well_part_number="0160-200-20",
            well_type="Mesoscope-style",
        ),
        IontophoresisInjection.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=expected_inj_anaesthetic,
            notes=None,
            injection_materials=None,
            injection_duration=None,
            recovery_time=None,
            workstation_id="SWS 3",
            instrument_id="Select...",
            injection_hemisphere=None,
            injection_coordinate_ml=-3.3,
            injection_coordinate_ap=-1.6,
            injection_coordinate_depth=None,
            injection_angle=0.0,
            injection_type="Iontophoresis",
            injection_current=5.0,
            alternating_current="7/7",
            injection_coordinate_reference=bregma_reference,
            bregma_to_lambda_distance=4.0,
        ),
        FiberImplant.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
            probes=[expected_probe1, expected_probe2],
        ),
        Craniotomy.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=expected_hp_anaesthetic,
            craniotomy_type=CraniotomyType.THREE_MM,
            craniotomy_hemisphere=None,
            craniotomy_coordinates_ml=2.8,
            craniotomy_coordinates_ap=1.3,
            craniotomy_size=3.0,
            dura_removed=None,
            workstation_id="SWS 3",
            notes=None,
            bregma_to_lambda_distance=4.0,
        ),
        # from list item 4
        Headframe.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
            anaesthesia=expected_hp_anaesthetic,
            headframe_type="Neuropixel-style",
            headframe_part_number="0160-100-10",
            well_part_number="0160-200-36",
            well_type="Neuropixel-style",
        ),
        Craniotomy.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=expected_hp_anaesthetic,
            craniotomy_type=CraniotomyType.OTHER,
            craniotomy_hemisphere=None,
            craniotomy_coordinates_ml=2.8,
            craniotomy_coordinates_ap=1.3,
            craniotomy_size=3.0,
            dura_removed=None,
            workstation_id="SWS 3",
            notes=None,
        ),
        # from list item 5
        Headframe.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
            anaesthesia=expected_hp_anaesthetic,
            headframe_type="WHC #42",
            headframe_part_number="42",
            well_part_number="0160-200-36",
            well_type="Neuropixel-style",
        ),
        # from list item 6
        Headframe.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
            anaesthesia=expected_hp_anaesthetic,
            headframe_type="NGC-style",
            headframe_part_number="0160-100-10",
            well_part_number=None,
            well_type=None,
        ),
        # from list item 7
        Craniotomy.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            anaesthesia=expected_hp_anaesthetic,
            craniotomy_type=None,
            craniotomy_hemisphere="Center",
            craniotomy_coordinates_ml=2.8,
            craniotomy_coordinates_ap=1.3,
            craniotomy_size=5.0,
            dura_removed=False,
            workstation_id="SWS 3",
            notes=None,
        ),
        Headframe.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
            anaesthesia=expected_hp_anaesthetic,
            headframe_type=None,
            headframe_part_number=None,
            well_part_number=None,
            well_type=None,
        ),
        # from list item 12
        SubjectProcedure.construct(
            start_date=datetime.date(2022, 12, 6),
            end_date=datetime.date(2022, 12, 6),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2115",
            animal_weight_prior=None,
            animal_weight_post=None,
            notes=None,
        ),
    ]

    expected_procedures1 = Procedures.construct(
        describedBy=described_by,
        schema_version="0.7.0",
        subject_id="650102",
        subject_procedures=expected_subject_procedures1,
    )

    expected_subject_procedures2 = [
        # from list item 8
        IontophoresisInjection.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            injection_coordinate_ml=-2.3,
            injection_coordinate_ap=4.72,
            injection_coordinate_depth=None,
            injection_angle=0.0,
            injection_hemisphere=Side.RIGHT,
            procedure_type="Iontophoresis",
            injection_current=5.0,
            alternating_current="7/7",
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
            instrument_id="Ionto #1",
            recovery_time=None,
            injection_materials=expected_inj_materials_1,
            injection_coordinate_reference=bregma_reference,
            bregma_to_lambda_distance=6.1,
        ),
        # from list item 9
        Headframe.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Headframe",
            headframe_type="Visual Ctx",
            headframe_part_number="0160-100-10",
            well_type="Mesoscope",
            well_part_number="0160-200-20",
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        Craniotomy.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Craniotomy",
            craniotomy_type="5mm",
            craniotomy_size=5.0,
            craniotomy_hemisphere=None,
            craniotomy_coordinates_ml=None,
            craniotomy_coordinates_ap=None,
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
            recovery_time=30,
            workstation_id="SWS 5",
            craniotomy_coordinates_reference=lambda_reference,
        ),
        # from list item 10
        Craniotomy.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Craniotomy",
            craniotomy_type="3mm",
            craniotomy_size=3.0,
            craniotomy_hemisphere=None,
            craniotomy_coordinates_ml=None,
            craniotomy_coordinates_ap=None,
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
            recovery_time=25,
        ),
        # from list item 11
        Headframe.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Headframe",
            headframe_type="WHC NP",
            headframe_part_number="0160-100-42",
            well_type="Neuropixel",
            well_part_number="0160-200-36",
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        NanojectInjection.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            injection_coordinate_ml=3.0,
            injection_coordinate_ap=-2.45,
            injection_coordinate_depth=None,
            injection_angle=None,
            procedure_type="Nanoject (Pressure)",
            injection_volume=500.0,
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
            recovery_time=25,
            injection_coordinate_reference=bregma_reference,
        ),
        NanojectInjection.construct(
            start_date=None,
            end_date=None,
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=28.2,
            animal_weight_post=None,
            injection_coordinate_ml=3.0,
            injection_coordinate_ap=-2.45,
            injection_coordinate_depth=None,
            injection_angle=None,
            procedure_type="Nanoject (Pressure)",
            injection_volume=600.0,
            anaesthesia=Anaesthetic(
                type="isoflurane", duration=120, level=2.5
            ),
            recovery_time=30,
            injection_coordinate_reference=bregma_reference,
        ),
        NanojectInjection.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Nanoject (Pressure)",
            injection_coordinate_ml=None,
            injection_coordinate_ap=None,
            injection_coordinate_depth=None,
            injection_angle=None,
            injection_volume=600.0,
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
            recovery_time=25,
            injection_coordinate_reference=bregma_reference,
        ),
        # from list item 14
        Headframe.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Headframe",
            headframe_type="Frontal Ctx",
            headframe_part_number="0160-100-46",
            well_type="WHC NP",
            well_part_number="0160-055-08",
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        NanojectInjection.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            injection_coordinate_ml=-5.2,
            injection_coordinate_ap=-0.85,
            injection_coordinate_depth=-3.1,
            injection_angle=0.0,
            injection_hemisphere=Side.LEFT,
            procedure_type="Nanoject (Pressure)",
            injection_volume=600.0,
            notes=None,
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
            recovery_time=25,
            injection_coordinate_reference=bregma_reference,
        ),
        FiberImplant.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            notes=None,
            procedure_type="Fiber implant",
            probes=OphysProbe.construct(
                name="Probe A",
                stereotactic_coordinate_ap=-0.85,
                stereotactic_coordinate_ml=-5.2,
                stereotactic_coordinate_dv=-2.95,
                angle=0.0,
                stereotactic_coordinate_reference=bregma_reference,
            ),
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        IontophoresisInjection.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            notes=None,
            procedure_type="Iontophoresis",
            injection_hemisphere=Side.LEFT,
            injection_coordinate_ml=-0.5,
            injection_coordinate_ap=2.0,
            injection_coordinate_depth=5.0,
            injection_angle=0.0,
            injection_current=None,
            alternating_current="7/7",
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
            recovery_time=25,
            injection_coordinate_reference=bregma_reference,
        ),
        FiberImplant.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            notes=None,
            procedure_type="Fiber implant",
            probes=OphysProbe.construct(
                name="Probe B",
                stereotactic_coordinate_ap=2.0,
                stereotactic_coordinate_ml=-0.5,
                stereotactic_coordinate_dv=-1.05,
                angle=0.0,
                stereotactic_coordinate_reference=bregma_reference,
            ),
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        IontophoresisInjection.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            injection_coordinate_ml=-2.2,
            injection_coordinate_ap=-6.1,
            injection_coordinate_depth=3.1,
            injection_angle=0.0,
            injection_hemisphere=Side.LEFT,
            procedure_type="Iontophoresis",
            injection_current=5.0,
            alternating_current="7/7",
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
            recovery_time=25,
            injection_coordinate_reference=bregma_reference,
        ),
        FiberImplant.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Fiber implant",
            probes=OphysProbe.construct(
                name="Probe C",
                stereotactic_coordinate_ap=-6.1,
                stereotactic_coordinate_ml=-2.2,
                stereotactic_coordinate_dv=-1.85,
                angle=0.0,
                stereotactic_coordinate_reference=bregma_reference,
            ),
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        IontophoresisInjection.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            injection_coordinate_ml=-2.5,
            injection_coordinate_ap=1.0,
            injection_coordinate_depth=3.0,
            injection_angle=0.0,
            injection_hemisphere=Side.RIGHT,
            procedure_type="Iontophoresis",
            injection_current=5.0,
            alternating_current="7/7",
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
            recovery_time=25,
            injection_coordinate_reference=bregma_reference,
        ),
        FiberImplant.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Fiber implant",
            probes=OphysProbe.construct(
                name="Probe D",
                stereotactic_coordinate_ap=1.0,
                stereotactic_coordinate_ml=-2.5,
                stereotactic_coordinate_dv=-1.8,
                angle=0.0,
                stereotactic_coordinate_reference=bregma_reference,
            ),
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        # from list item 15
        Headframe.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Headframe",
            headframe_type="Motor Ctx",
            headframe_part_number="0160-100-51",
            well_type="Scientifica (CAM)",
            well_part_number="Rev A",
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        # from list item 16
        Headframe.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Headframe",
            headframe_type="AI Straight Bar",
            headframe_part_number=None,
            well_type="No Well",
            well_part_number=None,
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        # from list item 17
        Headframe.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            procedure_type="Headframe",
            headframe_type="WHC 2P",
            headframe_part_number="0160-100-45",
            well_type="WHC 2P",
            well_part_number="0160-200-62",
            anaesthesia=Anaesthetic(type="isoflurane", duration=90, level=2.0),
        ),
        # from list item 13
        SubjectProcedure.construct(
            start_date=datetime.date(2022, 1, 3),
            end_date=datetime.date(2022, 1, 3),
            experimenter_full_name="NSB-187",
            iacuc_protocol="2103",
            animal_weight_prior=25.2,
            animal_weight_post=28.2,
            notes=None,
        ),
    ]

    expected_procedures_2023_1 = Procedures.construct(
        describedBy=described_by,
        schema_version="0.7.0",
        subject_id="650102",
        subject_procedures=expected_subject_procedures2,
    )


class TestSharepointClient(unittest.TestCase):
    """Class to test methods for SharePointClient."""

    client = SharePointClient(
        site_url="a_url", client_id="an_id", client_secret="a_secret"
    )

    def test_get_filter_string(self):
        """Tests that the filter string is constructed correctly."""
        version_2019 = self.client._get_filter_string(
            version=ListVersions.VERSION_2019, subject_id="652464"
        )
        version_2023 = self.client._get_filter_string(
            version=ListVersions.VERSION_2023, subject_id="652464"
        )
        expected_string1 = "substringof('652464', LabTracks_x0020_ID)"
        expected_string2 = "substringof('652464', LabTracks_x0020_ID1)"
        self.assertEqual(version_2019, expected_string1)
        self.assertEqual(version_2023, expected_string2)

    def test_map_response(self):
        """Tests that the responses are mapped as expected."""
        version_2019 = ListVersions.VERSION_2019
        version_2023 = ListVersions.VERSION_2023
        blank_ctx = ClientContext(base_url=self.client.site_url)
        list_item_collection_2019 = ListItemCollection(context=blank_ctx)
        list_item1 = ListItem(context=blank_ctx)
        list_item1.get_property = lambda x: Examples.list_item1_json[x]
        list_item_collection_2019.add_child(list_item1)

        list_item2 = ListItem(context=blank_ctx)
        list_item2.get_property = lambda x: Examples.list_item2_json[x]
        list_item_collection_2019.add_child(list_item2)

        list_item3 = ListItem(context=blank_ctx)
        list_item3.get_property = lambda x: Examples.list_item3_json[x]
        list_item_collection_2019.add_child(list_item3)

        list_item4 = ListItem(context=blank_ctx)
        list_item4.get_property = lambda x: Examples.list_item4_json[x]
        list_item_collection_2019.add_child(list_item4)

        list_item5 = ListItem(context=blank_ctx)
        list_item5.get_property = lambda x: Examples.list_item5_json[x]
        list_item_collection_2019.add_child(list_item5)

        list_item6 = ListItem(context=blank_ctx)
        list_item6.get_property = lambda x: Examples.list_item6_json[x]
        list_item_collection_2019.add_child(list_item6)

        list_item7 = ListItem(context=blank_ctx)
        list_item7.get_property = lambda x: Examples.list_item7_json[x]
        list_item_collection_2019.add_child(list_item7)

        # add list item with no procedure
        list_item12 = ListItem(context=blank_ctx)
        list_item12.get_property = lambda x: Examples.list_item12_json[x]
        list_item_collection_2019.add_child(list_item12)

        procedures2019 = self.client._map_response(
            version=version_2019,
            list_items=list_item_collection_2019,
        )

        list_item_collection_2023 = ListItemCollection(context=blank_ctx)
        list_item8 = ListItem(context=blank_ctx)
        list_item8.get_property = lambda x: Examples.list_item8_json[x]
        list_item_collection_2023.add_child(list_item8)

        list_item9 = ListItem(context=blank_ctx)
        list_item9.get_property = lambda x: Examples.list_item9_json[x]
        list_item_collection_2023.add_child(list_item9)

        list_item10 = ListItem(context=blank_ctx)
        list_item10.get_property = lambda x: Examples.list_item10_json[x]
        list_item_collection_2023.add_child(list_item10)

        list_item11 = ListItem(context=blank_ctx)
        list_item11.get_property = lambda x: Examples.list_item11_json[x]
        list_item_collection_2023.add_child(list_item11)

        # add list item with no procedure
        list_item13 = ListItem(context=blank_ctx)
        list_item13.get_property = lambda x: Examples.list_item13_json[x]
        list_item_collection_2023.add_child(list_item13)

        list_item14 = ListItem(context=blank_ctx)
        list_item14.get_property = lambda x: Examples.list_item14_json[x]
        list_item_collection_2023.add_child(list_item14)

        list_item15 = ListItem(context=blank_ctx)
        list_item15.get_property = lambda x: Examples.list_item15_json[x]
        list_item_collection_2023.add_child(list_item15)

        list_item16 = ListItem(context=blank_ctx)
        list_item16.get_property = lambda x: Examples.list_item16_json[x]
        list_item_collection_2023.add_child(list_item16)

        list_item17 = ListItem(context=blank_ctx)
        list_item17.get_property = lambda x: Examples.list_item17_json[x]
        list_item_collection_2023.add_child(list_item17)

        procedures2023 = self.client._map_response(
            version=version_2023,
            list_items=list_item_collection_2023,
        )
        self.assertCountEqual(
            Examples.expected_subject_procedures1, procedures2019
        )

        self.assertCountEqual(
            Examples.expected_subject_procedures2, procedures2023
        )

    def test_handle_response(self):
        """Tests that the responses returned are what's expected."""
        subject_id = "650102"
        empty_msg = self.client._handle_response_from_sharepoint(subject_id)
        empty_response = Responses.no_data_found_response()
        msg1 = self.client._handle_response_from_sharepoint(
            subject_id, Examples.expected_subject_procedures1
        )
        expected_msg1 = Responses.model_response(Examples.expected_procedures1)

        self.assertEqual(empty_response.status_code, empty_msg.status_code)
        self.assertEqual(empty_response.body, empty_msg.body)
        self.assertEqual(expected_msg1.body, msg1.body)

    def test_get_procedure_info(self):
        """Basic test on the main interface."""
        blank_ctx = ClientContext(base_url=self.client.site_url)
        list_item_collection = ListItemCollection(context=blank_ctx)
        list_item = ListItem(context=blank_ctx)
        list_item.to_json = lambda: Examples.list_item1_json
        list_item_collection.add_child(list_item)
        self.client.client_context.execute_query = lambda: list_item_collection
        response = self.client.get_procedure_info("0000")
        empty_response = Responses.no_data_found_response()

        self.assertEqual(response.status_code, empty_response.status_code)
        self.assertEqual(response.body, empty_response.body)


if __name__ == "__main__":
    unittest.main()
