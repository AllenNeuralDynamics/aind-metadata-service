"""Maps client objects from LAS Sharepoint database to internal AIND models."""

from typing import List

from aind_data_schema.core.procedures import Surgery
from office365.sharepoint.client_context import ClientContext

from aind_metadata_service.sharepoint.las2020.mapping import MappedLASList
from aind_metadata_service.sharepoint.las2020.models import LASList


class LAS2020Procedures:
    """Provides methods to retrieve procedure information from sharepoint,
    parses the response into an intermediate data model, and maps that model
    into AIND Procedures model."""

    @staticmethod
    def get_procedures_from_sharepoint(
        subject_id: str, client_context: ClientContext, list_title: str
    ) -> List[Surgery]:
        """
        Get list of Procedures from NSP database.
        Parameters
        ----------
        subject_id : str
          ID of the subject to find procedure information for
        client_context : ClientContext
          NSB Sharepoint client
        list_title : str
          Title of the list where the 2019 procedure data is stored
        Returns
        -------
        List[SubjectProcedure]
        """
        title_alias = LASList.model_fields.get("title").alias
        filter_string = f"substringof('{subject_id}', {title_alias})"
        list_view = client_context.web.lists.get_by_title(list_title)
        list_items = (
            list_view.items.paged(True)
            .top(100)
            .get()
            .filter(filter_string)
            .execute_query()
        )
        list_of_procedures = []
        for list_item in list_items:
            list_item_json = list_item.to_json()
            if subject_id in list_item_json[title_alias].split(" "):
                las_model = LASList.model_validate(list_item.to_json())
                mapped_model = MappedLASList(las=las_model)
                procedure = mapped_model.get_procedure(subject_id=subject_id)
                if procedure:
                    list_of_procedures.append(procedure)
        return list_of_procedures
