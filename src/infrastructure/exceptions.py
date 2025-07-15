"""Infrastructure layer exceptions with comprehensive error handling."""

from typing import Any


class InfrastructureError(Exception):
    """Base class for infrastructure-specific exceptions."""

    def __init__(self, message: str, details: dict[str, Any] | None = None, cause: Exception | None = None):
        """Initialize infrastructure error with context.

        Args:
            message: Human-readable error message
            details: Additional error context and debugging information
            cause: The underlying exception that caused this error

        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class RepositoryError(InfrastructureError):
    """Exception raised when repository operations fail."""

    def __init__(
        self,
        operation: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        cause: Exception | None = None,
    ):
        message = f"Repository {operation} failed"
        details = {"operation": operation}

        if entity_type:
            details["entity_type"] = entity_type
            message += f" for {entity_type}"

        if entity_id:
            details["entity_id"] = entity_id
            message += f" (ID: {entity_id})"

        super().__init__(message, details, cause)


class DataPersistenceError(InfrastructureError):
    """Exception raised when data persistence operations fail."""

    def __init__(self, operation: str, data_type: str | None = None, cause: Exception | None = None):
        message = f"Data persistence failed: {operation}"
        details = {"operation": operation}

        if data_type:
            details["data_type"] = data_type

        super().__init__(message, details, cause)


class CLIError(InfrastructureError):
    """Exception raised when CLI operations fail."""

    def __init__(self, command: str, args: list[str] | None = None, cause: Exception | None = None):
        message = f"CLI command failed: {command}"
        details = {"command": command}

        if args:
            details["args"] = args

        super().__init__(message, details, cause)


class CommandParsingError(CLIError):
    """Exception raised when command parsing fails."""

    def __init__(self, command: str, invalid_args: list[str] | None = None, cause: Exception | None = None):
        message = f"Failed to parse command: {command}"
        details = {"command": command}

        if invalid_args:
            details["invalid_args"] = invalid_args
            message += f" (Invalid arguments: {', '.join(invalid_args)})"

        super().__init__(command, invalid_args, cause)
        # Override the message and details from parent
        self.message = message
        self.details = details


class ServiceConfigurationError(InfrastructureError):
    """Exception raised when service configuration fails."""

    def __init__(self, service_name: str, configuration_step: str | None = None, cause: Exception | None = None):
        message = f"Service configuration failed: {service_name}"
        details = {"service_name": service_name}

        if configuration_step:
            details["configuration_step"] = configuration_step
            message += f" at step: {configuration_step}"

        super().__init__(message, details, cause)


class ResourceCleanupError(InfrastructureError):
    """Exception raised when resource cleanup fails."""

    def __init__(self, resource_type: str, resource_id: str | None = None, cause: Exception | None = None):
        message = f"Failed to cleanup resource: {resource_type}"
        details = {"resource_type": resource_type}

        if resource_id:
            details["resource_id"] = resource_id
            message += f" (ID: {resource_id})"

        super().__init__(message, details, cause)
