"""Module to create client to connect to sharepoint database"""

from enum import Enum
from typing import Optional

from aind_data_schema.procedures import (
    Procedures,
)
from dateutil import parser
from fastapi.responses import JSONResponse
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.client_object import ClientObject
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection

from aind_metadata_service.sharepoint.response_handler_2019 import NeurosurgeryAndBehaviorList2019
from aind_metadata_service.sharepoint.response_handler_2019 import ResponseHandler2019
from aind_metadata_service.sharepoint.response_handler_2023 import NeurosurgeryAndBehaviorList2023
from aind_metadata_service.sharepoint.response_handler_2023 import ResponseHandler2023

from aind_metadata_service.response_handler import Responses


class ListVersions(Enum):
    """Enum class to handle different SharePoint list versions."""

    VERSION_2023 = {
        "list_title": "SWR 2023-Present",
        "view_title": "New Request",
    }
    VERSION_2019 = {
        "list_title": "SWR 2018-Present",
        "view_title": "New Request",
    }


class SharePointClient:
    """This class contains the api to connect to SharePoint db."""

    def __init__(
        self, site_url: str, client_id: str, client_secret: str
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
        self.client_context = ClientContext(self.site_url).with_credentials(
            self.credentials
        )

    @staticmethod
    def _get_filter_string(version: ListVersions, subject_id: str) -> str:
        """
        Helper method to return a filter on the list
        Parameters
        ----------
        version : ListVersions
          Which version of the backend is being queried
        subject_id : str
          ID of the subject being queried for

        Returns
        -------
        str
          A string to pass into a query filter

        """
        default = (
            f"substringof("
            f"'{subject_id}', "
            f"{NeurosurgeryAndBehaviorList2019.ListField.LAB_TRACKS_ID.value}"
            f")"
        )
        version_2019 = (
            f"substringof("
            f"'{subject_id}', "
            f"{NeurosurgeryAndBehaviorList2019.ListField.LAB_TRACKS_ID.value}"
            f")"
        )
        version_2023 = (
            f"substringof("
            f"'{subject_id}', "
            f"{NeurosurgeryAndBehaviorList2023.ListField.LAB_TRACKS_ID.value}"
            f")"
        )
        filter_string = default
        if version == ListVersions.VERSION_2019:
            filter_string = version_2019
        elif version == ListVersions.VERSION_2023:
            filter_string = version_2023
        return filter_string

    def get_procedure_info(
        self,
        subject_id: str,
    ) -> JSONResponse:
        """
        Primary interface. Maps a subject_id to a response.
        Parameters
        ----------
        subject_id : str
          ID of the subject being queried for.

        Returns
        -------
        JSONResponse
          A response

        """
        # TODO: Add try to handle internal server error response.
        # default response
        for version in ListVersions:
            filter_string = self._get_filter_string(version, subject_id)
            ctx = self.client_context
            list_view = ctx.web.lists.get_by_title(
                version.value["list_title"]
            ).views.get_by_title(version.value["view_title"])
            ctx.load(list_view)
            ctx.execute_query()
            list_items = list_view.get_items().filter(filter_string)
            ctx.load(list_items)
            ctx.execute_query()
            response = self._handle_response_from_sharepoint(
                list_items, subject_id=subject_id, version=version
            )
        return response

    def _handle_response_from_sharepoint(  # noqa: C901
        self, list_items: ListItemCollection, subject_id: str, version: ListVersions
    ) -> JSONResponse:
        """
        Maps the response from SharePoint into a Procedures model
        Parameters
        ----------
        list_items : ListItemCollection
          SharePoint returns a ListItemCollection given a query
        subject_id : str
          ID of the subject being queried for.
        version: ListVersions
          Sharepoint DB version (2019,2023)

        Returns
        -------
        JSONResponse
          Either a Procedures model or an error response

        """
        if list_items:
            head_frames = []
            injections = []
            fiber_implants = []
            craniotomies = []
            if version == ListVersions.VERSION_2023:
                head_frames, injections, fiber_implants, craniotomies = ResponseHandler2023.handle_response_2023(
                    list_items, head_frames, injections, fiber_implants, craniotomies)
            else:
                head_frames, injections, fiber_implants, craniotomies = ResponseHandler2019.handle_response_2019(
                    list_items, head_frames, injections, fiber_implants, craniotomies
                )
            procedures = Procedures.construct(subject_id=subject_id)
            # before this was in loop for each list_item, is there a specific reason why?
            if head_frames:
                procedures.headframes = head_frames
            if injections:
                procedures.injections = injections
            if fiber_implants:
                procedures.fiber_implants = fiber_implants
            if craniotomies:
                procedures.craniotomies = craniotomies
            response = Responses.model_response(procedures)
        else:
            response = Responses.no_data_found_response()
        return response
