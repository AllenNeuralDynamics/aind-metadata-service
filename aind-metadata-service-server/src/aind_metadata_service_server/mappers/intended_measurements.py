"""Maps information to IntendedMeasurementInformation model."""

import logging
from typing import List

from aind_sharepoint_service_async_client.models import NSB2023List

from aind_metadata_service_server.mappers.nsb2023 import MappedNSBList
from aind_metadata_service_server.models import IntendedMeasurementInformation


class IntendedMeasurementMapper:
    """Class to handle mapping of data."""

    def __init__(
        self,
        nsb_2023: List[NSB2023List] = [],
        nsb_present: List[NSB2023List] = [],
    ):
        """
        Class constructor.
        Parameters
        ----------
        nsb_2023 : List[NSB2023List]
        nsb_present : List[NSBPresentList]
        """
        self.nsb_2023 = nsb_2023
        self.nsb_present = nsb_present

    def map_responses_to_intended_measurements(
        self, subject_id: str
    ) -> List[IntendedMeasurementInformation]:
        """
        Maps NSB2023 and NSB Present responses to intended measurements.

        Parameters
        ----------
        subject_id : str
            The subject ID for the measurements

        Returns
        -------
        List[IntendedMeasurementInformation]
            List of intended measurements
        """
        all_measurements = []
        if self.nsb_2023:
            for item in self.nsb_2023:
                mapper = MappedNSBList(item)
                measurements = mapper.get_intended_measurements()
                all_measurements.extend(measurements)
            logging.info(
                f"Found {len([m for m in all_measurements])} "
                f"measurements from NSB2023 for {subject_id}"
            )
        if self.nsb_present:
            for item in self.nsb_present:
                mapper = MappedNSBList(item)
                measurements = mapper.get_intended_measurements()
                all_measurements.extend(measurements)
            logging.info(
                f"Found {len(measurements)} measurements "
                f"from NSB Present for {subject_id}"
            )
        return all_measurements
