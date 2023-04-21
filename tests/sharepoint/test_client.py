"""Module to test SharePoint Client methods"""

import datetime
import json
import os
import unittest
from unittest.mock import patch, MagicMock
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
from aind_metadata_service.sharepoint.client import SharePointClient


class TestSharepointClient(unittest.TestCase):
    """Class to test methods for SharePointClient."""

    @patch("aind_metadata_service.sharepoint.client.ClientContext")
    def test_data_mapped(self, mock_sharepoint_client: MagicMock):

        inner_mock = MagicMock()
        mock_sharepoint_client.return_value.with_credentials.return_value = (
            inner_mock
        )
        mock_list_views = MagicMock()
        inner_mock.web.lists.get_by_title.return_value.views = mock_list_views
        mock_list_items = MagicMock()
        mock_list_views.get_by_title.return_value.get_items.return_value = (
            mock_list_items
        )
        # mock_list_items.filter.return_value = ["a", "b"]

        client = SharePointClient(nsb_site_url = "some_url",
                                  nsb_list_title_2019 = "some_list_title2019",
                                  nsb_list_title_2023 = "some_list_title2023",
                                  client_id = "some_client_id",
                                  client_secret = "some_client_secret")

        response = client.get_procedure_info(subject_id="12345")

    #
    # client = SharePointClient(
    #     site_url="a_url", client_id="an_id", client_secret="a_secret"
    # )
    #
    # def test_get_filter_string(self):
    #     """Tests that the filter string is constructed correctly."""
    #     version_2019 = self.client._get_filter_string(
    #         version=ListVersions.VERSION_2019, subject_id="652464"
    #     )
    #     version_2023 = self.client._get_filter_string(
    #         version=ListVersions.VERSION_2023, subject_id="652464"
    #     )
    #     expected_string1 = "substringof('652464', LabTracks_x0020_ID)"
    #     expected_string2 = "substringof('652464', LabTracks_x0020_ID1)"
    #     self.assertEqual(version_2019, expected_string1)
    #     self.assertEqual(version_2023, expected_string2)
    #
    # def test_map_response(self):
    #     """Tests that the responses are mapped as expected."""
    #     version_2019 = ListVersions.VERSION_2019
    #     version_2023 = ListVersions.VERSION_2023
    #     blank_ctx = ClientContext(base_url=self.client.site_url)
    #     list_item_collection_2019 = ListItemCollection(context=blank_ctx)
    #     list_item1 = ListItem(context=blank_ctx)
    #     list_item1.get_property = lambda x: Examples.list_item1_json[x]
    #     list_item_collection_2019.add_child(list_item1)
    #
    #     list_item2 = ListItem(context=blank_ctx)
    #     list_item2.get_property = lambda x: Examples.list_item2_json[x]
    #     list_item_collection_2019.add_child(list_item2)
    #
    #     list_item3 = ListItem(context=blank_ctx)
    #     list_item3.get_property = lambda x: Examples.list_item3_json[x]
    #     list_item_collection_2019.add_child(list_item3)
    #
    #     list_item4 = ListItem(context=blank_ctx)
    #     list_item4.get_property = lambda x: Examples.list_item4_json[x]
    #     list_item_collection_2019.add_child(list_item4)
    #
    #     list_item5 = ListItem(context=blank_ctx)
    #     list_item5.get_property = lambda x: Examples.list_item5_json[x]
    #     list_item_collection_2019.add_child(list_item5)
    #
    #     list_item6 = ListItem(context=blank_ctx)
    #     list_item6.get_property = lambda x: Examples.list_item6_json[x]
    #     list_item_collection_2019.add_child(list_item6)
    #
    #     list_item7 = ListItem(context=blank_ctx)
    #     list_item7.get_property = lambda x: Examples.list_item7_json[x]
    #     list_item_collection_2019.add_child(list_item7)
    #
    #     # add list item with no procedure
    #     list_item12 = ListItem(context=blank_ctx)
    #     list_item12.get_property = lambda x: Examples.list_item12_json[x]
    #     list_item_collection_2019.add_child(list_item12)
    #
    #     procedures2019 = self.client._map_response(
    #         version=version_2019,
    #         list_items=list_item_collection_2019,
    #     )
    #
    #     list_item_collection_2023 = ListItemCollection(context=blank_ctx)
    #     list_item8 = ListItem(context=blank_ctx)
    #     list_item8.get_property = lambda x: Examples.list_item8_json[x]
    #     list_item_collection_2023.add_child(list_item8)
    #
    #     list_item9 = ListItem(context=blank_ctx)
    #     list_item9.get_property = lambda x: Examples.list_item9_json[x]
    #     list_item_collection_2023.add_child(list_item9)
    #
    #     list_item10 = ListItem(context=blank_ctx)
    #     list_item10.get_property = lambda x: Examples.list_item10_json[x]
    #     list_item_collection_2023.add_child(list_item10)
    #
    #     list_item11 = ListItem(context=blank_ctx)
    #     list_item11.get_property = lambda x: Examples.list_item11_json[x]
    #     list_item_collection_2023.add_child(list_item11)
    #
    #     # add list item with no procedure
    #     list_item13 = ListItem(context=blank_ctx)
    #     list_item13.get_property = lambda x: Examples.list_item13_json[x]
    #     list_item_collection_2023.add_child(list_item13)
    #
    #     list_item14 = ListItem(context=blank_ctx)
    #     list_item14.get_property = lambda x: Examples.list_item14_json[x]
    #     list_item_collection_2023.add_child(list_item14)
    #
    #     list_item15 = ListItem(context=blank_ctx)
    #     list_item15.get_property = lambda x: Examples.list_item15_json[x]
    #     list_item_collection_2023.add_child(list_item15)
    #
    #     list_item16 = ListItem(context=blank_ctx)
    #     list_item16.get_property = lambda x: Examples.list_item16_json[x]
    #     list_item_collection_2023.add_child(list_item16)
    #
    #     list_item17 = ListItem(context=blank_ctx)
    #     list_item17.get_property = lambda x: Examples.list_item17_json[x]
    #     list_item_collection_2023.add_child(list_item17)
    #
    #     procedures2023 = self.client._map_response(
    #         version=version_2023,
    #         list_items=list_item_collection_2023,
    #     )
    #     self.assertCountEqual(
    #         Examples.expected_subject_procedures1, procedures2019
    #     )
    #
    #     self.assertCountEqual(
    #         Examples.expected_subject_procedures2, procedures2023
    #     )
    #
    # def test_handle_response(self):
    #     """Tests that the responses returned are what's expected."""
    #     subject_id = "650102"
    #     empty_msg = self.client._handle_response_from_sharepoint(subject_id)
    #     empty_response = Responses.no_data_found_response()
    #     msg1 = self.client._handle_response_from_sharepoint(
    #         subject_id, Examples.expected_subject_procedures1
    #     )
    #     expected_msg1 = Responses.model_response(Examples.expected_procedures1)
    #
    #     self.assertEqual(empty_response.status_code, empty_msg.status_code)
    #     self.assertEqual(empty_response.body, empty_msg.body)
    #     self.assertEqual(expected_msg1.body, msg1.body)
    #
    # def test_get_procedure_info(self):
    #     """Basic test on the main interface."""
    #     blank_ctx = ClientContext(base_url=self.client.site_url)
    #     list_item_collection = ListItemCollection(context=blank_ctx)
    #     list_item = ListItem(context=blank_ctx)
    #     list_item.to_json = lambda: Examples.list_item1_json
    #     list_item_collection.add_child(list_item)
    #     self.client.client_context.execute_query = lambda: list_item_collection
    #     response = self.client.get_procedure_info("0000")
    #     empty_response = Responses.no_data_found_response()
    #
    #     self.assertEqual(response.status_code, empty_response.status_code)
    #     self.assertEqual(response.body, empty_response.body)


if __name__ == "__main__":
    unittest.main()
