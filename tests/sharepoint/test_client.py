"""Module to test SharePoint Client methods"""

import json
import unittest
from pathlib import Path

from aind_data_schema.procedures import (
    Anaesthetic,
    FiberImplant,
    Headframe,
    IontophoresisInjection,
    NanojectInjection,
    Procedures,
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

    list_item1_filepath = (
        Path("tests") / "sharepoint" / "resources" / "list_item1.json"
    )
    with open(list_item1_filepath) as f:
        list_item1_json = json.load(f)

    list_item2_filepath = (
        Path("tests") / "sharepoint" / "resources" / "list_item2.json"
    )
    with open(list_item2_filepath) as f:
        list_item2_json = json.load(f)

    described_by = (
        "https://raw.githubusercontent.com/AllenNeuralDynamics/"
        "aind-data-schema/main/src/aind_data_schema/procedures.py"
    )

    expected_anaesthetic = Anaesthetic.construct(
        type="isoflurane",
        duration=None,
        level="Select...",
    )
    expected_procedures1 = Procedures.construct(
        describedBy=described_by,
        schema_version="0.5.2",
        subject_id="650102",
        headframes=(
            [
                Headframe.construct(
                    type=None,
                    start_date="2022-12-05T08:00:00Z",
                    end_date="2022-12-09T08:00:00Z",
                    experimenter_full_name="Mary Smith",
                    iacuc_protocol=None,
                    animal_weight=None,
                    notes=None,
                    well_part_number=None,
                    well_type=None,
                )
            ]
        ),
        injections=(
            [
                NanojectInjection.construct(
                    type=None,
                    start_date="2022-12-06",
                    end_date="2022-12-06",
                    experimenter_full_name="Mary Smith",
                    iacuc_protocol="2115",
                    animal_weight=None,
                    anaesthesia=expected_anaesthetic,
                    notes=None,
                    injection_materials=None,
                    injection_duration=5,
                    recovery_time=None,
                    workstation_id="SWS 3",
                    instrument_id="Select...",
                    injection_hemisphere="Left",
                    injection_coordinate_ml=-3.3,
                    injection_coordinate_ap=-1.6,
                    injection_coordinate_depth=4.3,
                    injection_angle=0.0,
                    injection_type="Nanoject (Pressure)",
                    injection_volume="400",
                )
            ]
        ),
        fiber_implants=(
            [
                FiberImplant.construct(
                    type=None,
                    start_date="2022-12-05T08:00:00Z",
                    end_date="2022-12-09T08:00:00Z",
                    experimenter_full_name="Mary Smith",
                    iacuc_protocol=None,
                    animal_weight=None,
                    notes=None,
                )
            ]
        ),
    )

    expected_procedures2 = Procedures.construct(
        describedBy=described_by,
        schema_version="0.5.2",
        subject_id="650102",
        headframes=(
            [
                Headframe.construct(
                    type=None,
                    start_date="2022-12-05T08:00:00Z",
                    end_date="2022-12-09T08:00:00Z",
                    experimenter_full_name="Mary Smith",
                    iacuc_protocol=None,
                    animal_weight=None,
                    notes=None,
                    well_part_number=None,
                    well_type=None,
                )
            ]
        ),
        injections=(
            [
                IontophoresisInjection.construct(
                    type=None,
                    start_date="2022-12-06",
                    end_date="2022-12-06",
                    experimenter_full_name="Mary Smith",
                    iacuc_protocol="2115",
                    animal_weight=None,
                    anaesthesia=expected_anaesthetic,
                    notes=None,
                    injection_materials=None,
                    injection_duration=5,
                    recovery_time=None,
                    workstation_id="SWS 3",
                    instrument_id="Select...",
                    injection_hemisphere="Right",
                    injection_coordinate_ml=-3.3,
                    injection_coordinate_ap=-1.6,
                    injection_coordinate_depth=4.3,
                    injection_angle=0.0,
                    injection_type="Iontophoresis",
                    injection_current="5uA",
                    alternating_current="7/7",
                )
            ]
        ),
        fiber_implants=(
            [
                FiberImplant.construct(
                    type=None,
                    start_date="2022-12-05T08:00:00Z",
                    end_date="2022-12-09T08:00:00Z",
                    experimenter_full_name="Mary Smith",
                    iacuc_protocol=None,
                    animal_weight=None,
                    notes=None,
                )
            ]
        ),
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
        default = self.client._get_filter_string(
            version=ListVersions.DEFAULT, subject_id="652464"
        )
        expected_string = "substringof('652464', LabTracks_x0020_ID)"
        self.assertEqual(version_2019, expected_string)
        self.assertEqual(default, expected_string)

    def test_handle_response(self):
        """Tests that the responses returned are what's expected."""
        subject_id = "650102"
        blank_ctx = ClientContext(base_url=self.client.site_url)
        list_item_collection = ListItemCollection(context=blank_ctx)
        # A completely empty list_item_collection
        empty_msg = self.client._handle_response_from_sharepoint(
            list_item_collection, subject_id=subject_id
        )

        # Add a list item with no procedures info
        list_item = ListItem(context=blank_ctx)
        list_item_collection.add_child(list_item)
        msg = self.client._handle_response_from_sharepoint(
            list_item_collection, subject_id=subject_id
        )
        expected_msg = Responses.model_response(
            Procedures.construct(subject_id=subject_id)
        )

        # Add a list item with contents
        list_item_collection = ListItemCollection(context=blank_ctx)
        list_item1 = ListItem(context=blank_ctx)
        list_item1.get_property = lambda x: Examples.list_item1_json[x]
        list_item_collection.add_child(list_item1)
        msg1 = self.client._handle_response_from_sharepoint(
            list_item_collection, subject_id=subject_id
        )
        expected_msg1 = Responses.model_response(Examples.expected_procedures1)
        empty_response = Responses.no_data_found_response()

        list_item_collection2 = ListItemCollection(context=blank_ctx)
        list_item2 = ListItem(context=blank_ctx)
        list_item2.get_property = lambda x: Examples.list_item2_json[x]
        list_item_collection2.add_child(list_item2)
        msg2 = self.client._handle_response_from_sharepoint(
            list_item_collection2, subject_id=subject_id
        )
        expected_msg2 = Responses.model_response(Examples.expected_procedures2)
        self.assertEqual(empty_response.status_code, empty_msg.status_code)
        self.assertEqual(empty_response.body, empty_msg.body)
        self.assertEqual(expected_msg.status_code, msg.status_code)
        self.assertEqual(expected_msg.body, msg.body)
        self.assertEqual(expected_msg1.status_code, msg1.status_code)
        self.assertEqual(expected_msg1.body, msg1.body)
        self.assertEqual(expected_msg2.body, msg2.body)

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
