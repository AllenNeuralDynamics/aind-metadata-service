import logging

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.mgi.client import MgiResponse
from aind_data_schema_models.pid_names import PIDName

from aind_metadata_service.response_handler import ModelResponse


class MgiMapper:

    def __init__(self, mgi_info: MgiResponse):

        self.mgi_info = mgi_info

    def get_model_response(self) -> ModelResponse:

        try:
            if len(self.mgi_info.summaryRows) == 0:
                return ModelResponse.no_data_found_error_response()
            first_summary_row = self.mgi_info.summaryRows[0]

            # 4 stars represent an exact match
            if first_summary_row.stars != "****" or first_summary_row.bestMatchType != "Synonym":
                return ModelResponse.no_data_found_error_response()

            pid_name = PIDName(name=first_summary_row.name, abbreviation=first_summary_row.bestMatchText)

            model_response = ModelResponse(aind_models=[pid_name], status_code=StatusCodes.DB_RESPONDED)
            return model_response
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()
