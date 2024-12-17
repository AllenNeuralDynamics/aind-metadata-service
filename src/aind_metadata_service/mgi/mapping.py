"""Module to handle mapping data from mgi to aind-data-schema models"""

import logging
import re
from typing import Union

from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.registries import Registry

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.mgi.client import MgiResponse
from aind_metadata_service.response_handler import ModelResponse


class MgiMapper:
    """Class that handles mapping mgi info"""

    DETAIL_URI_PATTERN = re.compile(r"/allele/MGI:(\d+)")

    def __init__(self, mgi_info: Union[MgiResponse, ModelResponse]):
        """Class constructor"""

        self.mgi_info = mgi_info

    def get_model_response(self) -> ModelResponse:
        """Get a model response from mgi ingo"""

        try:
            if isinstance(self.mgi_info, ModelResponse):
                return self.mgi_info

            if len(self.mgi_info.summaryRows) == 0:
                return ModelResponse.no_data_found_error_response()
            first_summary_row = self.mgi_info.summaryRows[0]

            # 4 stars represent an exact match
            if (
                first_summary_row.stars != "****"
                or first_summary_row.bestMatchType != "Synonym"
            ):
                return ModelResponse.no_data_found_error_response()

            if (
                re.match(self.DETAIL_URI_PATTERN, first_summary_row.detailUri)
                is not None
            ):
                registry_identifier = re.match(
                    self.DETAIL_URI_PATTERN, first_summary_row.detailUri
                ).group(1)
            else:
                registry_identifier = None

            pid_name = PIDName(
                name=first_summary_row.symbol,
                abbreviation=None,
                registry=Registry.MGI,
                registry_identifier=registry_identifier,
            )

            model_response = ModelResponse(
                aind_models=[pid_name], status_code=StatusCodes.DB_RESPONDED
            )
            return model_response
        except Exception as e:
            logging.exception(e)
            return ModelResponse.internal_server_error_response()
