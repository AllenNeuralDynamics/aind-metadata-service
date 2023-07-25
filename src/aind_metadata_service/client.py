"""Module for client library."""
from enum import Enum

import requests


class StatusCodes(Enum):
    """Enum class of status codes"""

    CONNECTION_ERROR = 503
    INTERNAL_SERVER_ERROR = 500
    MULTIPLE_RESPONSES = 300
    VALID_DATA = 200
    DB_RESPONDED = 203
    INVALID_DATA = 406
    NO_DATA_FOUND = 404
    MULTI_STATUS = 207


class AindMetadataServiceClient:
    """Class to handle client api calls to the service."""

    def __init__(self, domain: str):
        """
        Class constructor
        Parameters
        ----------
        domain : str
          url of the domain
        """

        self.domain = domain
        self.subject_url = f"{self.domain}/subject"
        self.procedures_url = f"{self.domain}/procedures"

    def get_subject(
        self, subject_id: str, pickle: bool = False
    ) -> requests.Response:
        """
        Retrieve a subject response from the server
        Parameters
        ----------
        subject_id : str
          id of the subject
        pickle: bool
          option to return pickled data instead of json
          TODO: Will be handled in future versions

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.subject_url, subject_id])
        with requests.get(url, params={"pickle": pickle}) as response:
            return response

    def get_procedures(
        self, subject_id: str, pickle: bool = False
    ) -> requests.Response:
        """
        Retrieve a procedures response from the server
        Parameters
        ----------
        subject_id : str
          id of the subject
        pickle: bool
          option to return pickled data instead of json
          TODO: Will be handled in future versions

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.procedures_url, subject_id])
        with requests.get(url, params={"pickle": pickle}) as response:
            return response
