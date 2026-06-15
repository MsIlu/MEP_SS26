from pydantic import BaseModel, ConfigDict


class PipelineModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )
