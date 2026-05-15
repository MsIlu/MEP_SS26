from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base configuration of every internal data model
    
    :param validate_assignment  unified validation
    :param extra    prevents unkown fields
    :param use_enum_values  
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )