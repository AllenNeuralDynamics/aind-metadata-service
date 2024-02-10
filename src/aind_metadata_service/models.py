from typing import Union

from aind_data_schema.core.procedures import (
    OtherSubjectProcedure,
    Surgery,
    TrainingProtocol,
    WaterRestriction,
)

SubjectProcedure = Union[
    Surgery, TrainingProtocol, WaterRestriction, OtherSubjectProcedure
]
