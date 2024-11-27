"""Module to retrieve data from TARS using session object"""

# Tools and Reagent Service

from requests import Response, Session

from aind_metadata_service.backends.tars.configs import Settings


class SessionHandler:
    """Handle session object to get data"""

    def __init__(
        self, session: Session, bearer_token: str, settings: Settings
    ):
        """Class constructor"""
        self.settings = settings
        self.session = session
        self.session.headers.update(
            {"Authorization": f"Bearer {bearer_token}"}
        )

    def get_prep_lot_response(self, prep_lot_id: str, page_size: int = 1) -> Response:
        """
        Requests data where the 'lots' field contains prep_lot_id
        Parameters
        ----------
        prep_lot_id : str
          Example, VT3214g
        page_size : int
          The search runs a contains query. Since we are mostly interested in
          exact matches, we set the default page size to 1.

        Returns
        -------
        Response

        """
        prep_lot_url = f"{self.settings.resource}/api/v1/ViralPrepLots"
        query_params = {
            "pageSize": "1",
            "order": "1",
            "orderBy": "id",
            "searchFields": "lot",
            "search": prep_lot_id,
        }
        response = self.session.get(url=prep_lot_url, params=query_params)
        return response

    def get_molecules_response(self, plasmid_name: str) -> Response:
        """
        Requests data where the 'name' field contains plasmid_name
        Parameters
        ----------
        plasmid_name : str
          Example, AiP1109

        Returns
        -------
        Response

        """

        molecule_url = f"{self.settings.resource}/api/v1/Molecules"
        query_params = {
            "order": "1",
            "orderBy": "id",
            "searchFields": "name",
            "search": plasmid_name,
        }
        response = self.session.get(url=molecule_url, params=query_params)
        return response
