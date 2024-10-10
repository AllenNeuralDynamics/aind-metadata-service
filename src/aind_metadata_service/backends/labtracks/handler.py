"""Module to retrieve data from LabTracks using session object"""

from typing import List, Union

from sqlalchemy.orm import aliased
from sqlmodel import Session, select

from aind_metadata_service.backends.labtracks.models import (
    AnimalsCommon,
    Groups,
    Species,
    Subject,
)


class SessionHandler:
    """Handle session object to get data"""

    def __init__(self, session: Session):
        """Class constructor"""
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
        # PyCharm raises warnings about the usage of the .label method
        # noinspection PyUnresolvedReferences
        statement = (
            select(
                ac.id,
                ac.class_values,
                ac.sex,
                ac.birth_date,
                s.species_name,
                ac.cage_id,
                ac.room_id,
                ac.paternal_index.label("paternal_id"),
                p.class_values.label("paternal_class_values"),
                ac.maternal_index.label("maternal_id"),
                m.class_values.label("maternal_class_values"),
                g.group_name,
                gm.group_description.label("group_description"),
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
