"""Centralized error handling and recovery mechanisms."""

import logging
from collections.abc import Callable
from typing import Any, TypeVar

from src.application.exceptions import ApplicationError
from src.domain.exceptions import DomainError
from src.infrastructure.exceptions import InfrastructureError

T = TypeVar("T")

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling with recovery mechanisms."""

    @staticmethod
    def handle_domain_error(error: DomainError, context: dict[str, Any] | None = None) -> None:
        """Handle domain-specific errors with appropriate logging and context.

        Args:
            error: The domain error to handle
            context: Additional context for error handling

        """
        context = context or {}
        message = getattr(error, "message", str(error))
        details = getattr(error, "details", {})

        logger.error(
            "Domain error occurred: %s",
            message,
            extra={
                "error_type": type(error).__name__,
                "error_details": details,
                "context": context,
            },
        )

    @staticmethod
    def handle_application_error(error: ApplicationError, context: dict[str, Any] | None = None) -> None:
        """Handle application-specific errors with appropriate logging and context.

        Args:
            error: The application error to handle
            context: Additional context for error handling

        """
        context = context or {}
        message = getattr(error, "message", str(error))
        details = getattr(error, "details", {})
        cause = getattr(error, "cause", None)

        logger.error(
            "Application error occurred: %s",
            message,
            extra={
                "error_type": type(error).__name__,
                "error_details": details,
                "context": context,
                "cause": str(cause) if cause else None,
            },
        )

    @staticmethod
    def handle_infrastructure_error(error: InfrastructureError, context: dict[str, Any] | None = None) -> None:
        """Handle infrastructure-specific errors with appropriate logging and context.

        Args:
            error: The infrastructure error to handle
            context: Additional context for error handling

        """
        context = context or {}
        logger.error(
            "Infrastructure error occurred: %s",
            error.message,
            extra={
                "error_type": type(error).__name__,
                "error_details": error.details,
                "context": context,
                "cause": str(error.cause) if error.cause else None,
            },
        )

    @staticmethod
    def handle_unexpected_error(error: Exception, context: dict[str, Any] | None = None) -> None:
        """Handle unexpected errors with appropriate logging and context.

        Args:
            error: The unexpected error to handle
            context: Additional context for error handling

        """
        context = context or {}
        logger.exception(
            "Unexpected error occurred: %s",
            str(error),
            extra={
                "error_type": type(error).__name__,
                "context": context,
            },
        )

    @staticmethod
    def with_error_handling(
        operation: Callable[[], T],
        context: dict[str, Any] | None = None,
        fallback_value: T | None = None,
        reraise: bool = True,
    ) -> T | None:
        """Execute an operation with comprehensive error handling.

        Args:
            operation: The operation to execute
            context: Additional context for error handling
            fallback_value: Value to return if operation fails and reraise is False
            reraise: Whether to reraise the exception after handling

        Returns:
            The result of the operation or fallback_value

        Raises:
            The original exception if reraise is True

        """
        try:
            return operation()
        except DomainError as e:
            ErrorHandler.handle_domain_error(e, context)
            if reraise:
                raise
            return fallback_value
        except ApplicationError as e:
            ErrorHandler.handle_application_error(e, context)
            if reraise:
                raise
            return fallback_value
        except InfrastructureError as e:
            ErrorHandler.handle_infrastructure_error(e, context)
            if reraise:
                raise
            return fallback_value
        except Exception as e:
            ErrorHandler.handle_unexpected_error(e, context)
            if reraise:
                raise
            return fallback_value

    @staticmethod
    def create_error_context(
        operation: str,
        component: str | None = None,
        user_id: str | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create standardized error context for consistent error reporting.

        Args:
            operation: The operation being performed
            component: The component where the error occurred
            user_id: The user ID if applicable
            request_id: The request ID if applicable
            **kwargs: Additional context information

        Returns:
            Standardized error context dictionary

        """
        context = {
            "operation": operation,
            "timestamp": logger.handlers[0].formatter.formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
            if logger.handlers
            else "unknown",
        }

        if component:
            context["component"] = component
        if user_id:
            context["user_id"] = user_id
        if request_id:
            context["request_id"] = request_id

        context.update(kwargs)
        return context


class RetryHandler:
    """Handles retry logic for operations that may fail temporarily."""

    @staticmethod
    def with_retry(
        operation: Callable[[], T],
        max_attempts: int = 3,
        retry_exceptions: tuple[type[Exception], ...] = (Exception,),
        context: dict[str, Any] | None = None,
    ) -> T:
        """Execute an operation with retry logic.

        Args:
            operation: The operation to execute
            max_attempts: Maximum number of retry attempts
            retry_exceptions: Tuple of exception types that should trigger a retry
            context: Additional context for error handling

        Returns:
            The result of the operation

        Raises:
            The last exception if all retry attempts fail

        """
        last_exception = None

        for attempt in range(max_attempts):
            try:
                return operation()
            except retry_exceptions as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    logger.warning(
                        "Operation failed (attempt %d/%d), retrying: %s",
                        attempt + 1,
                        max_attempts,
                        str(e),
                        extra={"context": context or {}},
                    )
                else:
                    logger.exception(
                        "Operation failed after %d attempts: %s",
                        max_attempts,
                        extra={"context": context or {}},
                    )

        # Re-raise the last exception if all attempts failed
        if last_exception:
            raise last_exception

        # This should never be reached, but included for type safety
        raise RuntimeError("Retry logic failed unexpectedly")
