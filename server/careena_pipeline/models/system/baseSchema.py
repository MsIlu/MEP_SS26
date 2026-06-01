from pydantic import BaseModel, ConfigDict

"""
Author @Freddy
    Base class for all Pydantic models in the system.

    Enforces:
    - strict validation (no extra fields)
    - assignment validation
    - consistent enum handling

    Pure infrastructure layer (no domain meaning).
"""
class BaseSchema(BaseModel):


    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )
