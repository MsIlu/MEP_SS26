from ..base.base import BaseSchema

"""
Data model to store demographic patient information

:param age 
:param biological_sex
:param pregnancy_status
"""
class Demographics(BaseSchema):
    age: int | None = None

    biological_sex: str | None = None

    pregnancy_status: bool | None = None