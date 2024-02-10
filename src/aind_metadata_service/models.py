from typing import get_args

from aind_data_schema.core.procedures import (
    Procedures
)

SubjectProcedure = get_args(get_args(Procedures.model_fields["subject_procedures"].annotation)[0])[0]
