"""Module that handles the methods to map the SmartSheet response to the
aind-data-schema Surgery model."""

import logging
import re
from typing import Optional
from decimal import Decimal
from aind_data_schema.core.procedures import Perfusion, Surgery
from pydantic import ValidationError
from aind_smartsheet_service_async_client.models import PerfusionsModel


class PerfusionMapper:
    """Class to handle mapping perfusion data"""

    IACUC_COL_PATTERN = re.compile(r"(\d+).*")
    ID_10_17504 = "dx.doi.org/10.17504/protocols.io.bg5vjy66"

    def __init__(self, smartsheet_perfusion: PerfusionsModel):
        """
        Class constructor.
        Parameters
        ----------
         smartsheet_perfusion: PerfusionsModel
        """
        self.smartsheet_perfusion = smartsheet_perfusion

    def _map_iacuc_protocol(
        self, iacuc_protocol_id: Optional[str]
    ) -> Optional[str]:
        """
        Parses the iacuc protocol number from a string. For example,
        '2109 - Analysis of brain - wide neural circuits in the mouse' is
        mapped to '2109'

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

    def map_to_aind_surgery(self) -> Surgery:
        """
        Map information to aind-data-schema Surgery. Will attempt to return
        a valid model. If there are any validation errors, then an invalid
        model will be returned.
        Returns
        -------
        Subject
        """
        smartsheet_perfusion = self.smartsheet_perfusion
        animal_weight_post = None
        anaesthesia = None
        protocol_id = self.ID_10_17504
        start_date = smartsheet_perfusion.var_date
        experimenter_full_name = smartsheet_perfusion.experimenter
        iacuc_protocol = self._map_iacuc_protocol(
            smartsheet_perfusion.iacuc_protocol
        )
        animal_weight_prior = (
            None
            if smartsheet_perfusion.animal_weight_prior__g is None
            else Decimal(smartsheet_perfusion.animal_weight_prior__g)
        )
        output_specimen_ids = (
            set()
            if smartsheet_perfusion.output_specimen_id_s is None
            else {str(int(float(smartsheet_perfusion.output_specimen_id_s)))}
        )
        notes = smartsheet_perfusion.notes

        try:
            return Surgery(
                start_date=start_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=anaesthesia,
                notes=notes,
                procedures=[
                    Perfusion(
                        output_specimen_ids=output_specimen_ids,
                        protocol_id=protocol_id,
                    )
                ],
            )
        except ValidationError as e:
            logging.warning(f"Validation error creating Surgery model: {e}")
            return Surgery.model_construct(
                start_date=start_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=anaesthesia,
                notes=notes,
                procedures=[
                    Perfusion.model_construct(
                        output_specimen_ids=output_specimen_ids,
                        protocol_id=protocol_id,
                    )
                ],
            )
