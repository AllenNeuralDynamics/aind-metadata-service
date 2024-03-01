""""""
from slims.internal import Record
from aind_data_schema.core.instrument import Instrument
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.client import StatusCodes
import json
from aind_metadata_service.slims.models import InstrumentTableRow
from aind_metadata_service.client import StatusCodes


class SlimsResponseHandler:
    """Handles SLIMS Response"""

    def map_slims_response_to_instrument(self, response):
        if response.status_code == 401:
            return ModelResponse.connection_error_response()
        elif response.status_code == 200:
            models = []
            for entity in response.json()["entities"]:
                attachment_response = self.get_attachment_response(entity)
                inst = Instrument.model_construct(**(attachment_response.json()))
                models.append(inst)
            return ModelResponse(aind_models=models, status_code=StatusCodes.DB_RESPONDED)


            # records = self.get_records(response)
            # models = []
            # for record in records:
            #     for attachment in record.attachments():
            #         attachment_response = self._get_attachment_json_response(attachment)
            #         # TODO: check filetype and that it is instrument json
            #         inst = Instrument.model_construct(**attachment_response)
            #         models.append(inst)
            return ModelResponse(aind_models=models, status_code=StatusCodes.DB_RESPONDED)

    @staticmethod
    def _get_attachment_json_response(attachment: Record):
        """Retrieves attachment as json response"""
        response = attachment.slims_api.get("repo/" + str(attachment.pk()))
        return json.loads(response.content)

    # def get_instrument_model_response(self):
    #     """Maps attachment to instrument model"""
    #     if self.record is None:
    #         return ModelResponse.internal_server_error_response()
    #     else:
    #         models = []
    #         for attachment in self.record.attachments():
    #             response = self._get_attachment_json_response(attachment)
    #             inst = Instrument.model_construct(**response)
    #             models.append(inst)
    #         return ModelResponse(aind_models=models, status_code=StatusCodes.DB_RESPONDED)
