"""Module to create client to connect to sharepoint database"""

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.listitems.collection import ListItemCollection

from enum import Enum
from aind_data_schema import Procedures


class NeurosurgeryAndBehaviorList2019:

    class ViewFields(Enum):
        ID = 'ID'
        LINK_TITLE = 'LinkTitle'
        PI = 'PI'
        IACUC_PROTOCOL = 'IACUC_x0020_Protocol_x0020__x002'
        PROJECT_ID = 'Project_x0020_ID_x0020__x0028_te',
        PROCEDURE = 'Procedure',
        LIMS_TASK_FLOW = 'LIMStaskflow1',
        DATE_RANGE_START = 'DateRangeStart',
        CREATED = 'Created',
        MODIFIED = 'Modified',
        EDITOR = 'Editor',
        LABTRACKS_GROUP = 'LabTracks_x0020_Group',
        REQUESTOR_COMMENTS = 'LongRequestorComments',
        IMPLANT_ID_COVER_SLIP_TYPE = 'ImplantIDCoverslipType'

    class ListFields(Enum):
        FILE_SYSTEM_OBJECT_TYPE = 'FileSystemObjectType'
        ID = 'Id'
        SERVER_REDIRECTED_EMBED_URI = 'ServerRedirectedEmbedUri'
        SERVER_REDIRECTED_EMBED_URL = 'ServerRedirectedEmbedUrl'
        CONTENT_TYPE_ID = 'ContentTypeId'
        TITLE = 'Title'
        PI_ID = 'PIId'
        PI_STRING_ID = 'PIStringId'
        LAB_TRACKS_REQUESTOR = 'LabTracks_x0020_Requestor'
        PROJECT_ID_TE = 'Project_x0020_ID_x0020__x0028_te'
        IACUC_PROTOCOL = 'IACUC_x0020_Protocol_x0020__x002'
        PROCEDURE = 'Procedure'
        LIGHT_CYCLE = 'Light_x0020_Cycle'
        LI_MS_REQUIRED = 'LIMs_x0020_Required'
        LAB_TRACKS_GROUP = 'LabTracks_x0020_Group'
        LAB_TRACKS_ID = 'LabTracks_x0020_ID'
        DATE_OF_SURGERY = 'Date_x0020_of_x0020_Surgery'
        LIMS_PROJECT_CODE = 'Lims_x0020_Project_x0020_Code'
        VIRUS_M_L = 'Virus_x0020_M_x002f_L'
        VIRUS_A_P = 'Virus_x0020_A_x002f_P'
        VIRUS_D_V = 'Virus_x0020_D_x002f_V'
        VIRUS_HEMISPHERE = 'Virus_x0020_Hemisphere'
        HP_M_L = 'HP_x0020_M_x002f_L'
        HP_A_P = 'HP_x0020_A_x002f_P'
        HP_DIAMETER = 'HP_x0020_Diameter'
        ISO_ON = 'Iso_x0020_On'
        CAGE = 'Cage'
        SEX = 'Sex'
        DATE_OF_BIRTH = 'Date_x0020_of_x0020_Birth'
        WEIGHT_BEFORE_SURGER = 'Weight_x0020_before_x0020_Surger'
        WEIGHT_AFTER_SURGERY = 'Weight_x0020_after_x0020_Surgery'
        PEDIGREE_NAME = 'PedigreeName'
        BREG2_LAMB = 'Breg2Lamb'
        HEADPOST_TYPE = 'HeadpostType'
        DATE_RANGE_START = 'DateRangeStart'
        DATE_RANGE_END = 'DateRangeEnd'
        HP_LOC = 'HpLoc'
        HP_PERF = 'HpPerf'
        HP_DUROTOMY = 'HPDurotomy'
        HP_PREV_INJECT = 'HpPrevInject'
        ML2ND_INJ = 'ML2ndInj'
        AP2ND_INJ = 'AP2ndInj'
        DV2ND_INJ = 'DV2ndInj'
        HEMISPHERE2ND_INJ = 'Hemisphere2ndInj'
        HP_WORK_STATION = 'HpWorkStation'
        SURGERY_STATUS = 'SurgeryStatus'
        COM_DUROTOMY = 'ComDurotomy'
        COM_SWELLING = 'ComSwelling'
        COM_SINUSBLEED = 'ComSinusbleed'
        COM_DURING1ST_INJ = 'ComDuring1stInj'
        COM_DURING2ND_INJ = 'ComDuring2ndInj'
        COM_DAMAGE = 'ComDamage'
        COM_WINDOW = 'ComWindow'
        COM_COPLANAR = 'ComCoplanar'
        COM_AFTER1ST_INJ = 'ComAfter1stInj'
        COM_AFTER2ND_INJ = 'ComAfter2ndInj'
        WORK_STATION1ST_INJECTION = 'WorkStation1stInjection'
        WORK_STATION2ND_INJECTION = 'WorkStation2ndInjection'
        DATE1ST_INJECTION = 'Date1stInjection'
        DATE2ND_INJECTION = 'Date2ndInjection'
        INJ1_STORAGE_LOCATION = 'Inj1StorageLocation'
        INJ2_STORAGE_LOCATION = 'Inj2StorageLocation'
        INJ1_TYPE = 'Inj1Type'
        INJ2_TYPE = 'Inj2Type'
        INJ1_VOL = 'Inj1Vol'
        INJ2_VOL = 'Inj2Vol'
        INJ1_LENGHTOF_TIME = 'Inj1LenghtofTime'
        INJ2_LENGHTOF_TIME = 'Inj2LenghtofTime'
        INJ1_CURRENT = 'Inj1Current'
        INJ2_CURRENT = 'Inj2Current'
        INJ1_ALTERNATING_TIME = 'Inj1AlternatingTime'
        INJ2_ALTERNATING_TIME = 'Inj2AlternatingTime'
        FIRST_INJECTION_WEIGHT_BEFOR = 'FirstInjectionWeightBefor'
        FIRST_INJECTION_WEIGHT_AFTER = 'FirstInjectionWeightAfter'
        FIRST_INJECTION_ISO_DURATION = 'FirstInjectionIsoDuration'
        SECOND_INJECTION_WEIGHT_BEFORE = 'SecondInjectionWeightBefore'
        SECOND_INJECTION_WEIGHT_AFTER = 'SecondInjectionWeightAfter'
        SECOND_INJECTION_ISO_DURATION = 'SecondInjectionIsoDuration'
        INJ1_ROUND = 'Inj1Round'
        INJ2_ROUND = 'Inj2Round'
        HP_ISO_LEVEL = 'HPIsoLevel'
        ROUND1_INJ_ISOLEVEL = 'Round1InjIsolevel'
        ROUND2_INJ_ISOLEVEL = 'Round2InjIsolevel'
        TEST1_ID = 'Test1Id'
        TEST1_STRING_ID = 'Test1StringId'
        TEST_2ND_ROUND_ID = 'TEST_x0020_2nd_x0020_Round_x0020Id'
        TEST_2ND_ROUND_STRING_ID = 'TEST_x0020_2nd_x0020_Round_x0020StringId'
        TEST_1ST_ROUND_ID = 'TEST_x0020_1st_x0020_Round_x0020Id'
        TEST_1ST_ROUND_STRING_ID = 'TEST_x0020_1st_x0020_Round_x0020StringId'
        ODATA_HP_REQUESTOR = 'OData__x0031_HP_x0020_Requestor_x0020_'
        ISSUE = 'Issue'
        TOUCH_UP_STATUS = 'Touch_x0020_Up_x0020_Status'
        TOUCH_UP_SURGEON_ID = 'Touch_x0020_Up_x0020_SurgeonId'
        TOUCH_UP_SURGEON_STRING_ID = 'Touch_x0020_Up_x0020_SurgeonStringId'
        TOUCH_UP_COMP = 'Touch_x0020_Up_x0020__x0020_Comp'
        EXUDATE_SEVERITY = 'Exudate_x0020_Severity'
        SCABBING = 'Scabbing'
        EYE_ISSUE = 'Eye_x0020_Issue'
        EYE_AFFECTED = 'Eye_x0020_Affected'
        TOUCH_UP_WEIGHT = 'Touch_x0020_Up_x0020_Weight_x002'
        LIMS_LINK = 'LIMS_x0020_link'
        HP_INJ = 'HP_x0020__x0026__x0020_Inj'
        FIELD30 = 'field30'
        FIELD50 = 'field50'
        LIM_STASKFLOW1 = 'LIMStaskflow1'
        COMPLIANCE_ASSET_ID = 'ComplianceAssetId'
        CREATED = 'Created'
        AUTHOR_ID = 'AuthorId'
        EDITOR_ID = 'EditorId'
        MODIFIED = 'Modified'
        HP_REQUESTOR_COMMENTS_PLAINTEXT = 'HPRequestorCommentsPlaintext'
        NANOJECT_NUMBER_INJ2 = 'NanojectNumberInj2'
        NANOJECT_NUMBER_INJ10 = 'NanojectNumberInj10'
        IONTO_NUMBER_INJ1 = 'IontoNumberInj1'
        IONTO_NUMBER_INJ2 = 'IontoNumberInj2'
        IONTO_NUMBER_HPINJ = 'IontoNumberHPINJ'
        INJ1VOLPERDEPTH = 'inj1volperdepth'
        INJ2VOLPERDEPTH = 'inj2volperdepth'
        INJ1ANGLE0 = 'Inj1angle0'
        INJ2ANGLE0 = 'Inj2angle0'
        CONTUSION = 'Contusion'
        HP_SURGEON_COMMENTS = 'HPSurgeonComments'
        ST_ROUND_INJECTION_COMMENTS = 'stRoundInjectionComments'
        ND_ROUNG_INJECTION_COMMENTS = 'ndRoungInjectionComments'
        FIRST_ROUND_IONTO_ISSUE = 'FirstRoundIontoIssue'
        HP_RECOVERY = 'HPRecovery'
        FIRST_INJ_RECOVERY = 'FirstInjRecovery'
        SECOND_INJ_RECOVER = 'SecondInjRecover'
        SECOND_ROUND_IONTO_ISSUE = 'SecondRoundIontoIssue'
        LONG_SURGEON_COMMENTS = 'LongSurgeonComments'
        LONG1ST_ROUND_INJ_CMTS = 'Long1stRoundInjCmts'
        LONG2ND_RND_INJ_CMTS = 'Long2ndRndInjCmts'
        LONG_REQUESTOR_COMMENTS = 'LongRequestorComments'
        INJ1_VIRUS_STRAIN_RT = 'Inj1VirusStrain_rt'
        INJ2_VIRUS_STRAIN_RT = 'Inj2VirusStrain_rt'
        RET_SETTING0 = 'retSetting0'
        RET_SETTING1 = 'retSetting1'
        START_OF_WEEK = 'Start_x0020_Of_x0020_Week'
        END_OF_WEEK = 'End_x0020_of_x0020_Week'
        AGE_AT_INJECTION = 'Age_x0020_at_x0020_Injection'
        CRANIOTOMY_TYPE = 'CraniotomyType'
        IMPLANT_ID_COVERSLIP_TYPE = 'ImplantIDCoverslipType'
        INJ1_ANGLE_V2 = 'Inj1Angle_v2'
        INJ2_ANGLE_V2 = 'Inj2Angle_v2'
        FIBER_IMPLANT1 = 'FiberImplant1'
        FIBER_IMPLANT1_DV = 'FiberImplant1DV'
        FIBER_IMPLANT2 = 'FiberImplant2'
        FIBER_IMPLANT2_DV = 'FiberImplant2DV'
        ID2 = 'ID'  # For some reason ID and Id are present in response
        ODATA_UI_VERSION_STRING = 'OData__UIVersionString'
        ATTACHMENTS = 'Attachments'
        GUID = 'GUID'


class ListVersions(Enum):
    VERSION_2019 = ({"list_title": "SWR 2019-Present",
                     "view_title": "New Request"})


class SharePointClient:
    """This class contains the api to connect to LabTracks db."""

    def __init__(
        self,
        site_url: str,
        client_id: str,
        client_secret: str
    ) -> None:
        """
        Initialize a client
        Parameters
        ----------
        site_url : str
           sharepoint site url
        client_id : str
            username for principal account to access sharepoint
        client_secret : str
            password for principal account to access sharepoint
        """
        self.site_url = site_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = ClientCredential(self.client_id, self.client_secret)
        self.client_context = (
            ClientContext(self.site_url).with_credentials(self.credentials)
        )

    @staticmethod
    def _get_filter_string(version, subject_id):
        default = (
            f"{NeurosurgeryAndBehaviorList2019.ListFields.LAB_TRACKS_ID.value}"
            f" eq {subject_id}"
        )
        # TODO: Handle other versions
        if version == ListVersions.VERSION_2019:
            filter_string = default
        else:
            filter_string = default
        return filter_string

    def get_procedure_info(self,
                           subject_id,
                           version=ListVersions.VERSION_2019):
        filter_string = self._get_filter_string(version, subject_id)
        ctx = self.client_context
        list_views = (
            ctx.web.lists.get_by_title(version.value["list_title"])
            .views.get_by_title(version.value["view_title"])
        )
        ctx.load(list_views)
        ctx.execute_query()
        list_items = list_views.get_items().filter(filter_string)
        ctx.load(list_items)
        ctx.execute_query()
        response = self._handle_response(list_items)

        return response

    def _handle_response(self, list_items: ListItemCollection) -> dict:
        if list_items:
            # TODO: Handle case where more than one item is returned?
            list_item = list_items[0]
            procedures = self._map_list_item_to_procedure(list_item)
            response = procedures
        else:
            response = {"message": "Nothing Found"}
        return response

    @staticmethod
    def _map_list_item_to_procedure(list_item: ListItem):
        subject_id = (
            list_item[(NeurosurgeryAndBehaviorList2019.
                       ListFields.LAB_TRACKS_ID.value)]
        )

        return Procedures(subject_id=subject_id)
