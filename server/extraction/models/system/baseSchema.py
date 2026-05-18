from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """
    BaseSchema is the technical foundation for all internal data models.

    It defines shared Pydantic configuration to ensure:
    - strict validation of inputs
    - prevention of unknown fields
    - consistent enum handling across the system

    This class has no domain meaning. It is purely infrastructural.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )