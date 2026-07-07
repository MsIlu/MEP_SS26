"""
Purpose: Shared error base for the core extraction path and parent type for specific LLM, JSON, and schema-related failures.
Input: extraction flow failure
Output: standardized core exception
Responsible: error grouping, shared error base, clear typing
Not responsible: error handling, retry logic, recovery
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
