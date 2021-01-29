import warnings
from typing import Optional

from pydantic import BaseModel, Field, validator


class WorkflowParams(BaseModel):
    """This set of parameters control what parts and how the workflow is run."""

    subject_id_to_use: Optional[str] = Field(
        None, description="[Deprecated] The column which identifies unique subjects.",
    )
    expected_sex_col_name: str = Field(
        "Expected_Sex", description="Column in the sample sheet that describes the expected sex."
    )

    remove_contam: bool = Field(
        True, description="Remove samples that exceed the contamination threshold."
    )
    remove_sex_discordant: bool = Field(
        True, description="Remove samples that have sex discorance."
    )
    remove_rep_discordant: bool = Field(
        True, description="Remove samples that have replicate discorance."
    )
    remove_unexpected_rep: bool = Field(
        True, description="Remove samples that are unexpected replicates."
    )

    minimum_pop_subjects: int = Field(
        50, description="Minimum number of subjects in a population", gt=0
    )
    control_hwp_threshold: int = Field(50, description="Control samples HWP threshold.", gt=0)

    @validator("subject_id_to_use")
    def validate_subject_id_to_use(cls, v):
        if v is None:
            return v

        warnings.warn(
            "subject_id_to_use is deprecated, add this to the Group_By column in the sample sheet.",
            DeprecationWarning,
        )

        return v