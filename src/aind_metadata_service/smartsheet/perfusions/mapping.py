"""Module that handles the methods to map the SmartSheet response to the
aind-data-schema Funding model."""

import logging
import re
from datetime import date
from typing import List, Optional

from aind_data_schema.core.procedures import Perfusion
from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.mapper import SmartSheetMapper
from aind_metadata_service.smartsheet.models import SheetRow
from aind_metadata_service.smartsheet.perfusions.models import (
    PerfusionProtocol,
    PerfusionsColumnNames,
)


class PerfusionsMapper(SmartSheetMapper):
    """Primary class to handle mapping data models and returning a response"""

    IACUC_COL_PATTERN = re.compile(r"(\d+).*")

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

    def _map_row_to_perfusion(
        self, row: SheetRow, input_subject_id: str
    ) -> Optional[Perfusion]:
        """
        Map a row to an optional perfusion model.
        Parameters
        ----------
        row : SheetRow
        input_subject_id : str
          The subject_id input by the user

        Returns
        -------
        Union[Perfusion, None]
          None if the subject_id in the row doesn't match the
          input_subject_id. Otherwise, will try to return a valid Perfusion
          model. If there is some data entry mistake, then it will return a
          Perfusion model as good as it can.

        """
        subject_id = None
        start_date = None
        end_date = None
        experimenter_full_name = None
        protocol_id = PerfusionProtocol.ID_10_17504
        iacuc_protocol = None
        animal_weight_prior = None
        animal_weight_post = None
        anaesthesia = None
        notes = None
        output_specimen_ids = set()

        for cell in row.cells:
            if (
                cell.columnId
                == self._column_id_map[PerfusionsColumnNames.SUBJECT_ID.value]
            ):
                subject_id = str(int(cell.value))
            if (
                cell.columnId
                == self._column_id_map[PerfusionsColumnNames.DATE.value]
            ):
                try:
                    start_date = date.fromisoformat(cell.value)
                except ValueError:
                    start_date = cell.value
                end_date = start_date
            if (
                cell.columnId
                == self._column_id_map[
                    PerfusionsColumnNames.EXPERIMENTER.value
                ]
            ):
                experimenter_full_name = cell.value
            if (
                cell.columnId
                == self._column_id_map[
                    PerfusionsColumnNames.IACUC_PROTOCOL.value
                ]
            ):
                iacuc_protocol = self._map_iacuc_protocol(cell.value)
            if (
                cell.columnId
                == self._column_id_map[
                    PerfusionsColumnNames.ANIMAL_WEIGHT_PRIOR.value
                ]
            ):
                animal_weight_prior = cell.value
            if (
                cell.columnId
                == self._column_id_map[
                    PerfusionsColumnNames.OUTPUT_SPECIMEN_ID.value
                ]
            ):
                output_specimen_ids = {str(int(cell.value))}
            if (
                cell.columnId
                == self._column_id_map[PerfusionsColumnNames.NOTES.value]
            ):
                notes = cell.value

        if input_subject_id != subject_id:
            return None
        else:
            try:
                return Perfusion(
                    start_date=start_date,
                    end_date=end_date,
                    experimenter_full_name=experimenter_full_name,
                    protocol_id=protocol_id,
                    iacuc_protocol=iacuc_protocol,
                    animal_weight_prior=animal_weight_prior,
                    animal_weight_post=animal_weight_post,
                    anaesthesia=anaesthesia,
                    notes=notes,
                    output_specimen_ids=output_specimen_ids,
                )
            except ValidationError:
                return Perfusion.model_construct(
                    start_date=start_date,
                    end_date=end_date,
                    experimenter_full_name=experimenter_full_name,
                    protocol_id=protocol_id,
                    iacuc_protocol=iacuc_protocol,
                    animal_weight_prior=animal_weight_prior,
                    animal_weight_post=animal_weight_post,
                    anaesthesia=anaesthesia,
                    notes=notes,
                    output_specimen_ids=output_specimen_ids,
                )

    def _get_perfusion_list(self, subject_id: str) -> List[Perfusion]:
        """
        Return a list of Perfusion information for a give subject_id.
        Parameters
        ----------
        subject_id : str
          The subject_id that the user inputs.

        Returns
        -------
        List[Perfusion]
          A list of Perfusion models. They might not necessarily pass
          validation checks.

        """
        rows_associated_with_subject_id: List[Perfusion] = []
        for row in self.model.rows:
            opt_perfusion: Optional[Perfusion] = self._map_row_to_perfusion(
                row=row, input_subject_id=subject_id
            )
            if opt_perfusion is not None:
                rows_associated_with_subject_id.append(opt_perfusion)
        return rows_associated_with_subject_id

    def get_model_response(self, input_id: str) -> ModelResponse:
        """
        Return a ModelResponse for a given id.
        Parameters
        ----------
        input_id : str
          The id with which to extract information

        Returns
        -------
        ModelResponse
          Will either be an internal server error response or a database
          responded response. Validation checks are performed downstream.

        """
        try:
            perfusion_list = self._get_perfusion_list(subject_id=input_id)
            return ModelResponse(
                aind_models=perfusion_list,
                status_code=StatusCodes.DB_RESPONDED,
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()
