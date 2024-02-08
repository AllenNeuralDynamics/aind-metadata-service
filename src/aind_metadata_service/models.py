from typing import Union

from aind_data_schema.core.procedures import Surgery, TrainingProtocol, WaterRestriction, OtherSubjectProcedure

SubjectProcedure = Union[Surgery, TrainingProtocol, WaterRestriction, OtherSubjectProcedure]