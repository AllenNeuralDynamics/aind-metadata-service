"""Module to create client to connect to sharepoint database"""

from aind_data_schema.procedures import (
    Procedures,
)
from fastapi.responses import JSONResponse
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

from aind_metadata_service.response_handler import Responses
from aind_metadata_service.sharepoint.nsb2019.client import ListClient


class SharePointClient:
    """This class contains the api to connect to SharePoint db."""

    def __init__(
        self, nsb_site_url: str, client_id: str, client_secret: str, nsb_2019_list_title: str
    ) -> None:
        """
        Initialize a client
        Parameters
        ----------
        nsb_site_url : str
           sharepoint site url
        client_id : str
            username for principal account to access sharepoint
        client_secret : str
            password for principal account to access sharepoint
        """
        self.nsb_site_url = nsb_site_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = ClientCredential(self.client_id, self.client_secret)
        self.nsb_client_context = (
            ClientContext(self.nsb_site_url).with_credentials(self.credentials)
        )
        self.nsb_2019_list_title = nsb_2019_list_title

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
        subject_procedures = []
        nsb_ctx = self.nsb_client_context
        nsb2019_list_client = ListClient(subject_id=subject_id, client_context=nsb_ctx, list_title=self.nsb_2019_list_title)
        procedures2019 = nsb2019_list_client.get_list_of_procedures()
        subject_procedures.extend(procedures2019)
        response = self._handle_response_from_sharepoint(
            subject_id=subject_id, subject_procedures=subject_procedures
        )
        return response

    @staticmethod
    def _handle_response_from_sharepoint(
        subject_id: str, subject_procedures=None
    ) -> JSONResponse:
        """
        Maps the response from SharePoint into a Procedures model
        Parameters
        ----------
        subject_id : str
          ID of the subject being queried for.
        subject_procedures: None/list

        Returns
        -------
        JSONResponse
          Either a Procedures model or an error response

        """
        if subject_procedures:
            procedures = Procedures.construct(subject_id=subject_id)
            procedures.subject_procedures = subject_procedures
            response = Responses.model_response(procedures)
        else:
            response = Responses.no_data_found_response()
        return response
