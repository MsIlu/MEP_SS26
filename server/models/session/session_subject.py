from ..base.base import BaseSchema

"""
Data model used to describe other persons mentioned by the user

:param person_id internal ID
:param temporary_label for example daughter / stranger
:param relationship_to_user describe relation to user
"""
class SessionSubject(BaseSchema):
    person_id: str | None = None

    temporary_label: str | None = None

    relationship_to_user: str | None = None