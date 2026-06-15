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
