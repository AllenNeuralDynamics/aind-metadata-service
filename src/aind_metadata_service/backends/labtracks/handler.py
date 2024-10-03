"""Module to retrieve data from LabTracks using session object"""

from aind_metadata_service.backends.labtracks.models import (
    Subject,
    AnimalsCommon,
    Groups,
    Species,
)
from typing import Union, List

from sqlmodel import select, Session
from sqlalchemy.orm import aliased


class SessionHandler:
    """Handle session object to get data"""

    def __init__(self, session: Session):
        self.session = session

    def get_subject_view(self, subject_id: Union[str, int]) -> List[Subject]:
        """
        Get a subject view from LabTracks by joining several tables.
        Parameters
        ----------
        subject_id : Union[str, int]
          ID of mouse to pull information about.

        Returns
        -------
        List[Subject]
          List of Subject models. If more than one row is returned, then this
          is likely due to an error with data entry into LabTracks.

        """
        ac = aliased(AnimalsCommon, name="ac")
        p = aliased(AnimalsCommon, name="p")
        m = aliased(AnimalsCommon, name="m")
        g = aliased(Groups, name="g")
        gm = aliased(Groups, name="gm")
        s = aliased(Species, name="s")
        statement = (
            select(
                ac.id,
                ac.class_values,
                ac.sex,
                ac.birth_date,
                s.species_name,
                ac.cage_id,
                ac.room_id,
                p.id,
                p.class_values,
                m.id,
                m.class_values,
                g.group_name,
                gm.group_description,
            )
            .where(ac.id == int(subject_id))
            .outerjoin(s, ac.species_id == s.id)
            .outerjoin(p, ac.paternal_index == p.id)
            .outerjoin(m, ac.maternal_index == m.id)
            .outerjoin(g, ac.group_id == g.id)
            .outerjoin(gm, m.group_id == gm.id)
        )
        results = self.session.execute(statement=statement)
        subject_models = [Subject.model_validate(r) for r in results]
        return subject_models


# router = APIRouter()
#
#
# @router.get(
#     "/subject/{subject_id}",
#     tags=["labtracks"],
#     response_description="Return HTTP Status Code 200 (OK)",
#     response_model=Subject,
# )
# async def get_subject(subject_id: str = Path(..., example="632269")):
#     """
#     ## LabTracks subject data
#     Retrieves subject information from LabTracks.
#     """
#     return Subject(id=subject_id)
