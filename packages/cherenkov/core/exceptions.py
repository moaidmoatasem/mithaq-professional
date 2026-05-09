"""Cherenkov exception hierarchy — every error is typed and catchable."""


class CherenkovError(Exception):
    """Base for all cherenkov exceptions."""


class ConfigurationError(CherenkovError):
    """Missing or invalid configuration."""


class MissingConfigError(ConfigurationError):
    """Required config key was not provided."""


class InvalidConfigError(ConfigurationError):
    """Config value failed validation."""


class SanitizationError(CherenkovError):
    """Data could not be safely sanitized."""


class RedactionError(SanitizationError):
    """Redaction engine failed to process data."""


class ValidationError(SanitizationError):
    """Sanitized payload failed schema validation."""


class OrchestrationError(CherenkovError):
    """Workflow or agent orchestration failure."""


class CognitiveLoopError(OrchestrationError):
    """Agent entered an infinite reasoning loop."""


class AgentError(OrchestrationError):
    """Agent instantiation or execution failed."""


class WorkflowError(OrchestrationError):
    """Workflow definition or execution error."""


class ScannerError(CherenkovError):
    """Scanner base error."""


class ScanFailedError(ScannerError):
    """Scanner execution failed."""


class ScannerNotFoundError(ScannerError):
    """Requested scanner is not registered."""


class StorageError(CherenkovError):
    """Database or persistence error."""
