"""Module to handle mapping Smartsheet funding model to AIND Funding model"""

import re
from typing import Optional

from aind_data_schema.core.procedures import Perfusion, Surgery
from pydantic import ValidationError

from aind_metadata_service.backends.smartsheet.models import PerfusionsModel


class Mapper:
    """Class to handle mapping data into Perfusions Surgery model."""

    def __init__(self, perfusions_model: PerfusionsModel):
        """Class constructor."""
        self.perfusions_model = perfusions_model

    IACUC_COL_PATTERN = re.compile(r"(\d+).*")
    PROTOCOL_ID = "dx.doi.org/10.17504/protocols.io.bg5vjy66"

    def _map_iacuc_protocol(
        self, iacuc_protocol_id: Optional[str]
    ) -> Optional[str]:
        """
        Parses the iacuc protocol number from a string. For example,
        '2109 - Analysis of brain - wide neural circuits in the mouse' is
        mapped to '2019'
        Parameters
        ----------
        iacuc_protocol_id : Optional[str]

        Returns
        -------
        Optional[str]

        """
        if iacuc_protocol_id is None:
            return None
        elif self.IACUC_COL_PATTERN.match(iacuc_protocol_id):
            return self.IACUC_COL_PATTERN.match(iacuc_protocol_id).group(1)
        else:
            return iacuc_protocol_id

    def map_to_perfusions(self) -> Surgery:
        """Map perfusions from Smartsheet to aind-data-schema Surgery model."""

        start_date = self.perfusions_model.date
        experimenter_full_name = self.perfusions_model.experimenter
        iacuc_protocol = self._map_iacuc_protocol(
            self.perfusions_model.iacuc_protocol
        )
        animal_weight_prior = self.perfusions_model.animal_weight_prior
        anaesthesia = None
        animal_weight_post = None
        notes = None
        output_specimen_ids = (
            set()
            if self.perfusions_model.output_specimen_id is None
            else {str(int(self.perfusions_model.output_specimen_id))}
        )

        try:
            return Surgery(
                start_date=start_date,
                protocol_id=self.PROTOCOL_ID,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=anaesthesia,
                notes=notes,
                procedures=[
                    Perfusion(
                        output_specimen_ids=output_specimen_ids,
                        protocol_id=self.PROTOCOL_ID,
                    )
                ],
            )
        except ValidationError:
            return Surgery.model_construct(
                start_date=start_date,
                protocol_id=self.PROTOCOL_ID,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=anaesthesia,
                notes=notes,
                procedures=[
                    Perfusion(
                        output_specimen_ids=output_specimen_ids,
                        protocol_id=self.PROTOCOL_ID,
                    )
                ],
            )
