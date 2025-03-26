"""Module for client library."""

from enum import Enum
from typing import Optional

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
    UNPROCESSIBLE_ENTITY = 422
    BAD_REQUEST = 400


class CustomClientMeta(type):
    """Metaclass to write custom error message for class constructor."""

    def __call__(cls, *args, **kwargs):
        """On init"""
        if not args and not kwargs:
            raise TypeError(
                "You must specify the server domain. "
                "If you're onsite at the Allen Institute, "
                "the production domain is http://aind-metadata-service "
                "and the dev domain is http://aind-metadata-service-dev"
            )
        return super().__call__(*args, **kwargs)


class AindMetadataServiceClient(metaclass=CustomClientMeta):
    """Class to handle client api calls to the service."""

    def __init__(self, domain: str):
        """
        Initialize client with required domain parameter.

        Parameters
        ----------
        domain : str
            REQUIRED. The domain/base URL of the metadata service.
            Common values:
            * Allen internal prod: "http://aind-metadata-service"
            * Allen internal dev: "http://aind-metadata-service-dev"

            Example:
            >>> client = AindMetadataServiceClient("http://aind-metadata-service") # noqa: E501
        """

        self.domain = domain

        self.subject_url = f"{self.domain}/subject"
        self.procedures_url = f"{self.domain}/procedures"
        self.injection_materials_url = (
            f"{self.domain}/tars_injection_materials"
        )
        self.intended_measurements_url = f"{self.domain}/intended_measurements"
        self.ecephys_sessions_url = (
            f"{self.domain}/ecephys_sessions_by_subject"
        )
        self.protocols_url = f"{self.domain}/protocols"
        self.mgi_allele_url = f"{self.domain}/mgi_allele"
        self.perfusions_url = f"{self.domain}/perfusions"
        self.funding_url = f"{self.domain}/funding"
        self.project_names_url = f"{self.domain}/project_names"
        self.smartspim_imaging_url = f"{self.domain}/slims/smartspim_imaging"
        self.histology_url = f"{self.domain}/slims/histology"

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
        with requests.get(url, params={}) as response:
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
        with requests.get(url, params={}) as response:
            return response

    def get_intended_measurements(self, subject_id: str) -> requests.Response:
        """
        Retrieve intended measurements for a subject from the server
        Parameters
        ----------
        subject_id : str
          id of the subject

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.intended_measurements_url, subject_id])
        with requests.get(url, params={}) as response:
            return response

    def get_injection_materials(
        self, prep_lot_number: str
    ) -> requests.Response:
        """
        Retrieve injection materials from the server
        Parameters
        ----------
        prep_lot_number : str
          preparation lot number

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.injection_materials_url, prep_lot_number])
        with requests.get(url, params={}) as response:
            return response

    def get_ecephys_sessions(self, subject_id: str) -> requests.Response:
        """
        Retrieve ecephys sessions for a subject from the server
        Parameters
        ----------
        subject_id : str
          id of the subject

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.ecephys_sessions_url, subject_id])
        with requests.get(url, params={}) as response:
            return response

    def get_protocols(self, protocol_name: str) -> requests.Response:
        """
        Retrieve protocols information from the server
        Parameters
        ----------
        protocol_name : str
          name of the protocol

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.protocols_url, protocol_name])
        with requests.get(url, params={}) as response:
            return response

    def get_mgi_allele(self, allele_name: str) -> requests.Response:
        """
        Retrieve MGI allele information from the server
        Parameters
        ----------
        allele_name : str
          name of the allele

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.mgi_allele_url, allele_name])
        with requests.get(url, params={}) as response:
            return response

    def get_perfusions(self, subject_id: str) -> requests.Response:
        """
        Retrieve perfusion information for a subject from the server
        Parameters
        ----------
        subject_id : str
          id of the subject

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.perfusions_url, subject_id])
        with requests.get(url, params={}) as response:
            return response

    def get_funding(self, project_name: str) -> requests.Response:
        """
        Retrieve funding information for a project from the server
        Parameters
        ----------
        project_name : str
          name of the project

        Returns
        -------
        requests.Response

        """
        url = "/".join([self.funding_url, project_name])
        with requests.get(url, params={}) as response:
            return response

    def get_project_names(self) -> requests.Response:
        """
        Retrieve all project names from the server

        Returns
        -------
        requests.Response

        """
        with requests.get(self.project_names_url, params={}) as response:
            return response

    def get_smartspim_imaging(
        self,
        subject_id: Optional[str] = None,
        start_date_gte: Optional[str] = None,
        end_date_lte: Optional[str] = None,
    ) -> requests.Response:
        """
        Retrieve SmartSPIM imaging data from the server

        Parameters
        ----------
        subject_id : str, optional
          id of the subject
        start_date_gte : str, optional
          start date (ISO format)
        end_date_lte : str, optional
          end date (ISO format)

        Returns
        -------
        requests.Response

        """
        params = {}
        if subject_id:
            params["subject_id"] = subject_id
        if start_date_gte:
            params["start_date_gte"] = start_date_gte
        if end_date_lte:
            params["end_date_lte"] = end_date_lte

        with requests.get(
            self.smartspim_imaging_url, params=params
        ) as response:
            return response

    def get_histology(
        self,
        subject_id: Optional[str] = None,
        start_date_gte: Optional[str] = None,
        end_date_lte: Optional[str] = None,
    ) -> requests.Response:
        """
        Retrieve histology data from the server

        Parameters
        ----------
        subject_id : str, optional
          id of the subject
        start_date_gte : str, optional
          start date (ISO format)
        end_date_lte : str, optional
          end date (ISO format)

        Returns
        -------
        requests.Response

        """
        params = {}
        if subject_id:
            params["subject_id"] = subject_id
        if start_date_gte:
            params["start_date_gte"] = start_date_gte
        if end_date_lte:
            params["end_date_lte"] = end_date_lte

        with requests.get(self.histology_url, params=params) as response:
            return response
