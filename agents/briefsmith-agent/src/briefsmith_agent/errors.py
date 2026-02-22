"""Custom exceptions for user-facing CLI failures."""


class BriefsmithAgentError(Exception):
    """Base error type for the application."""


class InputValidationError(BriefsmithAgentError):
    """Raised when input arguments or file validation fails."""


class FileReadError(BriefsmithAgentError):
    """Raised when input file cannot be read."""


class OutputWriteError(BriefsmithAgentError):
    """Raised when output markdown cannot be written."""
