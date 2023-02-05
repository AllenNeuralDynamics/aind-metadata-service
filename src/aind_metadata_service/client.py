"""Module for client library."""
import requests


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

    def get_subject(self, subject_id: str) -> requests.Response:
        """
        Retrieve a subject response from the server
        Parameters
        ----------
        subject_id : str
          id of the subject

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.subject_url, subject_id])
        with requests.get(url) as response:
            return response

    def get_procedures(self, subject_id: str) -> requests.Response:
        """
        Retrieve a procedures response from the server
        Parameters
        ----------
        subject_id : str
          id of the subject

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.procedures_url, subject_id])
        with requests.get(url) as response:
            return response
