"""Module to test SharePoint Client methods"""

import unittest

from aind_data_schema.procedures import (
    FiberImplant,
    Headframe,
    Injection,
    Procedures,
)
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.listitems.listitem import ListItem

from aind_metadata_service.sharepoint.client import (
    ListVersions,
    SharePointClient,
)


class Examples:
    """Class to hold some examples to compare against"""

    lims_link = "<a href='http://lims2/specimens?search650102'>Search</a>"
    project_id = "122-01-001-10 Neural Dynamics Scientific Activities"
    # TODO: Move this to JSON file in resources
    list_item_json = {
        "FileSystemObjectType": 0,
        "Id": 5554,
        "ServerRedirectedEmbedUri": None,
        "ServerRedirectedEmbedUrl": "",
        "ContentTypeId": "0x0100D7F25D3C051CD548B3304044B3DA2E96",
        "Title": "650102HP+Injection+Optic Fiber Implant",
        "PIId": 5313,
        "PIStringId": "5313",
        "LabTracks_x0020_Requestor": "Mary Smith",
        "Project_x0020_ID_x0020__x0028_te": project_id,
        "IACUC_x0020_Protocol_x0020__x002": "2115",
        "Procedure": "HP+Injection+Optic Fiber Implant",
        "Light_x0020_Cycle": "Reverse (9pm to 9am)",
        "LIMs_x0020_Required": "No",
        "LabTracks_x0020_Group": "Slc6a3-Cre",
        "LabTracks_x0020_ID": "650102",
        "Date_x0020_of_x0020_Surgery": "2022-12-06T08:00:00Z",
        "Lims_x0020_Project_x0020_Code": "Select...",
        "Virus_x0020_M_x002f_L": "-3.3",
        "Virus_x0020_A_x002f_P": "-1.6",
        "Virus_x0020_D_x002f_V": "4.3",
        "Virus_x0020_Hemisphere": "Left",
        "HP_x0020_M_x002f_L": None,
        "HP_x0020_A_x002f_P": None,
        "HP_x0020_Diameter": "5mm",
        "Iso_x0020_On": None,
        "Cage": None,
        "Sex": "Select...",
        "Date_x0020_of_x0020_Birth": None,
        "Weight_x0020_before_x0020_Surger": None,
        "Weight_x0020_after_x0020_Surgery": None,
        "PedigreeName": "Slc6a3-Cre-650102",
        "Breg2Lamb": None,
        "HeadpostType": "AI Straight Headbar",
        "DateRangeStart": "2022-12-05T08:00:00Z",
        "DateRangeEnd": "2022-12-09T08:00:00Z",
        "HpLoc": "Select...",
        "HpPerf": "Select if applicable...",
        "HPDurotomy": "Select...",
        "HpPrevInject": "Select...",
        "ML2ndInj": "-0.6",
        "AP2ndInj": "-3.05",
        "DV2ndInj": "4.3",
        "Hemisphere2ndInj": "Left",
        "HpWorkStation": "SWS 3",
        "SurgeryStatus": "New",
        "ComDurotomy": "Select...",
        "ComSwelling": "Select...",
        "ComSinusbleed": "Select...",
        "ComDuring1stInj": "Select...",
        "ComDuring2ndInj": "Select...",
        "ComDamage": "Select...",
        "ComWindow": "Select...",
        "ComCoplanar": "Select...",
        "ComAfter1stInj": "Select...",
        "ComAfter2ndInj": "Select...",
        "WorkStation1stInjection": "SWS 3",
        "WorkStation2ndInjection": "Select...",
        "Date1stInjection": "2022-12-06T08:00:00Z",
        "Date2ndInjection": None,
        "Inj1StorageLocation": "A Box",
        "Inj2StorageLocation": "A Box",
        "Inj1Type": "Nanoject (Pressure)",
        "Inj2Type": "Nanoject (Pressure)",
        "Inj1Vol": "400",
        "Inj2Vol": "400",
        "Inj1LenghtofTime": None,
        "Inj2LenghtofTime": None,
        "Inj1Current": None,
        "Inj2Current": None,
        "Inj1AlternatingTime": None,
        "Inj2AlternatingTime": None,
        "FirstInjectionWeightBefor": None,
        "FirstInjectionWeightAfter": None,
        "FirstInjectionIsoDuration": None,
        "SecondInjectionWeightBefore": None,
        "SecondInjectionWeightAfter": None,
        "SecondInjectionIsoDuration": None,
        "Inj1Round": "1st",
        "Inj2Round": "1st",
        "HPIsoLevel": "Select...",
        "Round1InjIsolevel": "Select...",
        "Round2InjIsolevel": "Select...",
        "Test1Id": 2916,
        "Test1StringId": "2916",
        "TEST_x0020_2nd_x0020_Round_x0020Id": None,
        "TEST_x0020_2nd_x0020_Round_x0020StringId": None,
        "TEST_x0020_1st_x0020_Round_x0020Id": 2916,
        "TEST_x0020_1st_x0020_Round_x0020StringId": "2916",
        "OData__x0031_HP_x0020_Requestor_x0020_": None,
        "Issue": "Select...",
        "Touch_x0020_Up_x0020_Status": "Select...",
        "Touch_x0020_Up_x0020_SurgeonId": None,
        "Touch_x0020_Up_x0020_SurgeonStringId": None,
        "Touch_x0020_Up_x0020__x0020_Comp": None,
        "Exudate_x0020_Severity": "Select...",
        "Scabbing": "Select...",
        "Eye_x0020_Issue": "Select...",
        "Eye_x0020_Affected": "Select...",
        "Touch_x0020_Up_x0020_Weight_x002": None,
        "LIMS_x0020_link": lims_link,
        "HP_x0020__x0026__x0020_Inj": "Yes",
        "field30": "23",
        "field50": "23",
        "LIMStaskflow1": None,
        "ComplianceAssetId": None,
        "Created": "2022-12-02T17:04:37Z",
        "AuthorId": 187,
        "EditorId": 2916,
        "Modified": "2022-12-02T18:15:36Z",
        "HPRequestorCommentsPlaintext": None,
        "NanojectNumberInj2": "Select...",
        "NanojectNumberInj10": "Select...",
        "IontoNumberInj1": "Select...",
        "IontoNumberInj2": "Select...",
        "IontoNumberHPINJ": None,
        "inj1volperdepth": None,
        "inj2volperdepth": None,
        "Inj1angle0": "Select...",
        "Inj2angle0": "Select...",
        "Contusion": "Select...",
        "HPSurgeonComments": None,
        "stRoundInjectionComments": None,
        "ndRoungInjectionComments": None,
        "FirstRoundIontoIssue": "Select...",
        "HPRecovery": None,
        "FirstInjRecovery": None,
        "SecondInjRecover": None,
        "SecondRoundIontoIssue": "Select...",
        "LongSurgeonComments": None,
        "Long1stRoundInjCmts": None,
        "Long2ndRndInjCmts": None,
        "LongRequestorComments": None,
        "Inj1VirusStrain_rt": "Premixied &quot;\u200bdL+Cre&quot;",
        "Inj2VirusStrain_rt": "DIO-ChrimsonR",
        "retSetting0": "Off",
        "retSetting1": "Off",
        "Start_x0020_Of_x0020_Week": "2022-12-05T08:00:00Z",
        "End_x0020_of_x0020_Week": "2022-12-09T08:00:00Z",
        "Age_x0020_at_x0020_Injection": "44901.0000000000",
        "CraniotomyType": None,
        "ImplantIDCoverslipType": None,
        "Inj1Angle_v2": "0",
        "Inj2Angle_v2": "0",
        "FiberImplant1": False,
        "FiberImplant1DV": "4.2",
        "FiberImplant2": False,
        "FiberImplant2DV": "4.2",
        "ID": 5554,
        "OData__UIVersionString": "4.0",
        "Attachments": False,
        "GUID": "00c3c333-c4a0-42aa-adab-88183c324201",
    }

    described_by = (
        "https://raw.githubusercontent.com/AllenNeuralDynamics/"
        "aind-data-schema/main/site-packages/aind_data_schema/procedures.py"
    )
    expected_procedures1 = Procedures.construct(
        describedBy=described_by,
        schema_version="0.4.3",
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
                Injection.construct(
                    type=None,
                    start_date="2022-12-05T08:00:00Z",
                    end_date="2022-12-09T08:00:00Z",
                    experimenter_full_name="Mary Smith",
                    iacuc_protocol=None,
                    animal_weight=None,
                    notes=None,
                    injection_materials=None,
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
        expected_string = "substringof(652464, LabTracks_x0020_ID)"
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
        expected_msg = Procedures.construct(subject_id=subject_id)

        # Add a list item with contents
        list_item_collection = ListItemCollection(context=blank_ctx)
        list_item2 = ListItem(context=blank_ctx)
        list_item2.get_property = lambda x: Examples.list_item_json[x]
        list_item_collection.add_child(list_item2)
        msg1 = self.client._handle_response_from_sharepoint(
            list_item_collection, subject_id=subject_id
        )
        self.assertEqual({"message": "Nothing Found"}, empty_msg)
        self.assertEqual(expected_msg, msg)
        self.assertEqual(Examples.expected_procedures1, msg1)

    def test_get_procedure_info(self):
        """Basic test on the main interface."""
        blank_ctx = ClientContext(base_url=self.client.site_url)
        list_item_collection = ListItemCollection(context=blank_ctx)
        list_item = ListItem(context=blank_ctx)
        list_item.to_json = lambda: Examples.list_item_json
        list_item_collection.add_child(list_item)
        self.client.client_context.execute_query = lambda: list_item_collection
        response = self.client.get_procedure_info("0000")
        self.assertEqual(response, {"message": "Nothing Found"})


if __name__ == "__main__":
    unittest.main()
