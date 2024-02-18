"""Maps client objects from NSB Sharepoint database to internal AIND models."""

from typing import List

from aind_data_schema.core.procedures import Surgery
from office365.sharepoint.client_context import ClientContext

from aind_metadata_service.sharepoint.nsb2023.mapping import MappedNSBList
from aind_metadata_service.sharepoint.nsb2023.models import NSBList


class NSB2023Procedures:
    """Provides methods to retrieve procedure information from sharepoint,
    parses the response into an intermediate data model, and maps that model
    into AIND Procedures model."""

    _view_title = "New Request"

    def get_procedures_from_sharepoint(
        self, subject_id: str, client_context: ClientContext, list_title: str
    ) -> List[Surgery]:
        """
        Get list of Procedures from NSB 2019 database.
        Parameters
        ----------
        subject_id : str
          ID of the subject to find procedure information for
        client_context : ClientContext
          NSB Sharepoint client
        list_title : str
          Title of the list where the 2023 procedure data is stored
        Returns
        -------
        List[SubjectProcedure]
        """

        labtrack_alias = NSBList.model_fields.get("lab_tracks_id1").alias
        filter_string = f"{labtrack_alias} eq '{subject_id}'"
        list_view = client_context.web.lists.get_by_title(
            list_title
        ).views.get_by_title(self._view_title)
        client_context.load(list_view)
        client_context.execute_query()
        list_items = list_view.get_items().filter(filter_string)
        client_context.load(list_items)
        client_context.execute_query()
        list_of_procedures = []
        for list_item in list_items:
            nsb_model = NSBList.model_validate(list_item.to_json())
            mapped_model = MappedNSBList(nsb=nsb_model)
            procedure = mapped_model.get_procedure()
            list_of_procedures.extend(procedure)
        return list_of_procedures
