"""
Author @Freddy
    Base exception for extraction-related failures.
    Sub categories are used to determine the type of error
    for future error handling like retries, fallback etc.
"""
class ExtractionError(Exception):

    pass


class EmptyLLMResponseError(ExtractionError):
    pass


class InvalidJSONError(ExtractionError):
    pass


class SchemaValidationError(ExtractionError):
    pass


class LLMRequestError(ExtractionError):
    pass
