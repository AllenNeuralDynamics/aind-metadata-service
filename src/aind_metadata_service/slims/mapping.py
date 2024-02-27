""""""
from slims.internal import Record
from aind_data_schema.core.instrument import Instrument
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.client import StatusCodes
import json
from aind_metadata_service.slims.models import InstrumentTableRow


class SlimsResponseHandler:
    """Handles SLIMS Response"""

    def __init__(self, record: Record):
        self.record = record

    @staticmethod
    def _get_attachment_json_response(attachment: Record):
        """Retrieves attachment as json response"""
        response = attachment.slims_api.get("repo/" + str(attachment.pk()))
        return json.loads(response.content)

    def get_instrument_model_response(self):
        """Maps attachment to instrument model"""
        if self.record is None:
            return ModelResponse.internal_server_error_response()
        else:
            models = []
            for attachment in self.record.attachments():
                response = self._get_attachment_json_response(attachment)
                inst = Instrument.model_construct(**response)
                models.append(inst)
            # TODO: create a generic model from table info if no attachments
            return ModelResponse(aind_models=models, status_code=StatusCodes.DB_RESPONDED)
