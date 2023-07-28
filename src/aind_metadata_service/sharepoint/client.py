"""Module to create client to connect to sharepoint database"""

import logging
from typing import List, Optional

from aind_data_schema.procedures import Procedures
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.sharepoint.nsb2019.procedures import (
    NSB2019Procedures,
)
from aind_metadata_service.sharepoint.nsb2023.procedures import (
    NSB2023Procedures,
)


class SharePointClient:
    """This class contains the api to connect to SharePoint db."""

    def __init__(
        self,
        nsb_site_url: str,
        client_id: str,
        client_secret: str,
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
        self.nsb_client_context = ClientContext(
            self.nsb_site_url
        ).with_credentials(self.credentials)

    def get_procedure_info(
        self,
        subject_id: str,
        list_title: str,
    ) -> ModelResponse:
        """
        Primary interface. Maps a subject_id to a response.
        Parameters
        ----------
        subject_id : str
          ID of the subject being queried for.
        list_title: str
          Title of the sharepoint list to retrieve Procedures records

        Returns
        -------
        ModelResponse
          Either an internal_error response or a ModelResponse with a list
          of Procedures models

        """
        try:
            nsb_ctx = self.nsb_client_context
            # There's probably a cleaner way to switch on this.
            mapper = (
                NSB2019Procedures()
                if "2019" in list_title
                else NSB2023Procedures()
            )
            subj_procedures = mapper.get_procedures_from_sharepoint(
                subject_id=subject_id,
                client_context=nsb_ctx,
                list_title=list_title,
            )
            procedures = self._handle_response_from_sharepoint(
                subject_id=subject_id, subject_procedures=subj_procedures
            )
            procedures = [] if procedures is None else [procedures]
            return ModelResponse(
                aind_models=procedures, status_code=StatusCodes.DB_RESPONDED
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    @staticmethod
    def _handle_response_from_sharepoint(
        subject_id: str, subject_procedures: Optional[list] = None
    ) -> Optional[Procedures]:
        """
        Maps the response from SharePoint into a Procedures model
        Parameters
        ----------
        subject_id : str
          ID of the subject being queried for.
        subject_procedures: Optional[list]
          An optional list of subject_procedures.

        Returns
        -------
        Optional[Procedures]
          A Procedures model if subject_procedures, else None.

        """
        if subject_procedures:
            procedures = Procedures.construct(subject_id=subject_id)
            procedures.subject_procedures = subject_procedures
            return procedures
        else:
            return None

    @staticmethod
    def _merge_procedures(
        left_procedures: List[Procedures], right_procedures: List[Procedures]
    ) -> List[Procedures]:
        """
        Merges two lists of Procedures. Given the way the lists are
        constructed, the length of the lists will either be 0 or 1.
        Parameters
        ----------
        left_procedures : List[Procedures]
        right_procedures : List[Procedures]

        Returns
        -------
        List[Procedures]
          Single model with the subject_procedures merged from both lists.

        """
        if len(left_procedures) == 0:
            return right_procedures
        elif len(right_procedures) == 0:
            return left_procedures
        else:
            subject_id = left_procedures[0].subject_id
            new_subject_procedures = (
                left_procedures[0].subject_procedures
                + right_procedures[0].subject_procedures
            )
            return [
                Procedures.construct(
                    subject_id=subject_id,
                    subject_procedures=new_subject_procedures,
                )
            ]

    def _merge_two_responses(
        self,
        left_model_response: ModelResponse[Procedures],
        right_model_response: ModelResponse[Procedures],
    ) -> ModelResponse[Procedures]:
        """
        Merges two ModelResponses of Procedures type.
        Parameters
        ----------
        left_model_response : ModelResponse[Procedures]
        right_model_response : ModelResponse[Procedures]

        Returns
        -------
        ModelResponse[Procedures]
          A merged response.

        """
        if (
            left_model_response.status_code.value >= 500
            and right_model_response.status_code.value >= 500
        ):
            return ModelResponse.internal_server_error_response()
        elif (
            left_model_response.status_code == StatusCodes.DB_RESPONDED
            and right_model_response.status_code.value >= 500
        ):
            return ModelResponse(
                aind_models=left_model_response.aind_models,
                status_code=StatusCodes.MULTI_STATUS,
                message=(
                    "There was an error retrieving records from one or more "
                    "of the databases."
                ),
            )
        elif (
            left_model_response.status_code.value >= 500
            and right_model_response.status_code == StatusCodes.DB_RESPONDED
        ):
            return ModelResponse(
                aind_models=right_model_response.aind_models,
                status_code=StatusCodes.MULTI_STATUS,
                message=(
                    "There was an error retrieving records from one or more "
                    "of the databases."
                ),
            )
        else:
            left_procedures: List[Procedures] = left_model_response.aind_models
            right_procedures: List[
                Procedures
            ] = right_model_response.aind_models
            procedures = self._merge_procedures(
                left_procedures=left_procedures,
                right_procedures=right_procedures,
            )
            return ModelResponse(
                aind_models=procedures, status_code=StatusCodes.DB_RESPONDED
            )

    def merge_responses(
        self, model_responses: List[ModelResponse[Procedures]]
    ) -> ModelResponse[Procedures]:
        """
        Merges a list of ModelResponses into a single ModelResponse using a
        left-scan operation.
        Parameters
        ----------
        model_responses : List[ModelResponse[Procedures]]

        Returns
        -------
        ModelResponse[Procedures]

        """
        if len(model_responses) == 0:
            return ModelResponse.internal_server_error_response()
        else:
            model_response = model_responses[0]
            for next_response in model_responses[1:]:
                model_response = self._merge_two_responses(
                    model_response, next_response
                )
            return model_response
