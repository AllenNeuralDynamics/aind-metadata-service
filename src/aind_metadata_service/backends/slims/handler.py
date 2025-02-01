"""Module to handle SLIMS responses"""

import logging
from typing import Any, Dict, Optional

from aind_slims_api import SlimsClient
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models import SlimsInstrumentRdrc
from slims import criteria


class SessionHandler:
    """Handle session object to get data"""

    def __init__(self, session: SlimsClient):
        """Class constructor"""
        self.session = session

    def get_instrument_attachment(
        self, input_id: str, partial_match: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch an instrument attachment from SLIMS.
        Parameters
        ----------
        input_id : str
          ID of the rig or instrument to fetch.
        partial_match : bool
          If True, fetch the closest match to input id.
          If False, fetch exact match.

        Returns
        -------
        Optional[Dict[str, Any]]

        """

        try:
            if partial_match:
                record = self.session.fetch_model(
                    SlimsInstrumentRdrc,
                    criteria.contains("name", input_id),
                )
                attachment = self.session.fetch_attachment(record=record)
            else:
                record = self.session.fetch_model(
                    model=SlimsInstrumentRdrc, name=input_id
                )
                attachment = self.session.fetch_attachment(
                    record=record, name=input_id
                )
            if attachment:
                attachment_response = self.session.fetch_attachment_content(
                    attachment=attachment
                )
                attachment_response.raise_for_status()
                return attachment_response.json()
            else:
                logging.warning(
                    f"Attachment not found for input_id {input_id} and "
                    f"partial match {partial_match}"
                )
                return None
        except SlimsRecordNotFound:
            logging.warning(
                f"Slims record not found for input_id {input_id} and "
                f"partial match {partial_match}"
            )
            return None
