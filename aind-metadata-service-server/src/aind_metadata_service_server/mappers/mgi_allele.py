"""Module to handle mapping data from mgi to aind-data-schema models"""

import logging
import re
from typing import Optional

from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.registries import Registry
from aind_mgi_service_async_client.models import MgiSummaryRow
from pydantic import ValidationError


class MgiMapper:
    """Class that handles mapping mgi info"""

    DETAIL_URI_PATTERN = re.compile(r"/allele/MGI:(\d+)")

    def __init__(self, mgi_summary_row: MgiSummaryRow):
        """
        Class constructor
        Parameters
        ----------
        mgi_summary_row : MgiSummaryRow
            Single MGI summary row to map
        """
        self.mgi_summary_row = mgi_summary_row

    def map_to_aind_pid_name(self) -> Optional[PIDName]:
        """
        Map a MgiSummaryRow to an optional PIDName model.

        Returns
        -------
        PIDName | None
            None if no valid PIDName can be created,
            otherwise a PIDName model with parsed data.
        """
        summary_row = self.mgi_summary_row
        if (
            summary_row.stars != "****"
            or summary_row.best_match_type != "Synonym"
        ):
            return None

        registry_identifier = None
        if summary_row.detail_uri:
            match = re.match(self.DETAIL_URI_PATTERN, summary_row.detail_uri)
            if match:
                registry_identifier = match.group(1)

        if not summary_row.symbol:
            return None

        try:
            return PIDName(
                name=summary_row.symbol,
                abbreviation=None,
                registry=Registry.MGI,
                registry_identifier=registry_identifier,
            )
        except ValidationError as e:
            logging.warning(f"Validation error creating PIDName model: {e}")
            return PIDName.model_construct(
                name=summary_row.symbol,
                abbreviation=None,
                registry=Registry.MGI,
                registry_identifier=registry_identifier,
            )
