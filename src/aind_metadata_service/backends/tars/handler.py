"""Module to retrieve data from TARS using session object"""

# Tools and Reagent Service
import json
from typing import List

from requests import Response, Session

from aind_metadata_service.backends.tars.configs import Settings
from aind_metadata_service.backends.tars.models import (
    MoleculeData,
    MoleculeResponse,
    PrepLotData,
    PrepLotResponse,
)


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

    @staticmethod
    def _sanitize_input(input_id: str) -> str:
        """
        Removes leading and trailing spaces from user input.
        >>> SessionHandler._sanitize_input('\tVT3214g ')
        'VT3214g'
        Parameters
        ----------
        input_id : str

        Returns
        -------
        str
        """
        return input_id.strip()

    def _get_raw_prep_lot_response(
        self, prep_lot_id: str, page_size: int
    ) -> Response:
        """
        Get raw requests Response
        Parameters
        ----------
        prep_lot_id : str
        page_size : int
          The search runs a contains query. Since we are mostly interested in
          exact matches, we set the default page size to 1.

        Returns
        -------
        Response
        """

        prep_lot_url = f"{self.settings.resource}/api/v1/ViralPrepLots"
        query_params = {
            "pageSize": str(page_size),
            "order": "1",
            "orderBy": "id",
            "searchFields": "lot",
            "search": prep_lot_id,
        }

        return self.session.get(url=prep_lot_url, params=query_params)

    def _get_prep_lot_response(
        self, prep_lot_id: str, page_size: int = 1
    ) -> PrepLotResponse:
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
        PrepLotResponse

        """

        response = self._get_raw_prep_lot_response(
            prep_lot_id=prep_lot_id, page_size=page_size
        )
        response.raise_for_status()
        model_response = PrepLotResponse.model_validate_json(
            json.dumps(response.json())
        )

        return model_response

    def get_prep_lot_data(self, prep_lot_id: str) -> List[PrepLotData]:
        """
        Return prep_lot_data for a prep_lot_id
        Parameters
        ----------
        prep_lot_id : str

        Returns
        -------
        List[PrepLotData]
        """
        sanitized_id = self._sanitize_input(prep_lot_id)
        response = self._get_prep_lot_response(prep_lot_id=sanitized_id)
        prep_lot_data = []
        for d in response.data:
            if isinstance(d.lot, str) and d.lot.strip() == sanitized_id:
                prep_lot_data.append(d)
        return prep_lot_data

    def _get_raw_molecules_response(self, plasmid_name: str) -> Response:
        """
        Get raw requests Response
        Parameters
        ----------
        plasmid_name : str
                page_size : int
          The search runs a contains query. Since we are mostly interested in
          exact matches, we set the default page size to 1.

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

        return self.session.get(url=molecule_url, params=query_params)

    def _get_molecule_response(self, plasmid_name: str) -> MoleculeResponse:
        """
        Requests data where the 'name' field contains plasmid_name
        Parameters
        ----------
        plasmid_name : str
          Example, AiP1109

        Returns
        -------
        MoleculeResponse

        """

        response = self._get_raw_molecules_response(plasmid_name=plasmid_name)
        response.raise_for_status()
        model_response = MoleculeResponse.model_validate_json(
            json.dumps(response.json())
        )
        return model_response

    def get_molecule_data(self, plasmid_name: str) -> List[MoleculeData]:
        """
        Return prep_lot_data for a prep_lot_id
        Parameters
        ----------
        plasmid_name : str

        Returns
        -------
        List[MoleculeData]
        """
        sanitized_id = self._sanitize_input(plasmid_name)
        response = self._get_molecule_response(plasmid_name=sanitized_id)
        molecule_data = []
        for d in response.data:
            for a in d.aliases:
                if isinstance(a.name, str) and a.name == sanitized_id:
                    molecule_data.append(d)
                    break
                else:
                    continue
        return molecule_data
