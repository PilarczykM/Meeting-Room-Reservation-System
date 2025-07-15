"""Tests for error handling utilities."""

from unittest.mock import patch

import pytest

from src.application.exceptions import ApplicationError
from src.domain.exceptions import DomainError
from src.infrastructure.error_handler import ErrorHandler, RetryHandler
from src.infrastructure.exceptions import InfrastructureError


def test_handle_domain_error(self):
    """Test handling domain errors."""
    error = DomainError("Test domain error", {"field": "value"})
    context = {"operation": "test"}

    with patch("src.infrastructure.error_handler.logger") as mock_logger:
        ErrorHandler.handle_domain_error(error, context)

        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        assert "Domain error occurred" in args[0]
        assert error.message in args[1]


def test_handle_application_error(self):
    """Test handling application errors."""
    cause = Exception("Root cause")
    error = ApplicationError("Test application error", {"field": "value"}, cause)
    context = {"operation": "test"}

    with patch("src.infrastructure.error_handler.logger") as mock_logger:
        ErrorHandler.handle_application_error(error, context)

        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        assert "Application error occurred" in args[0]
        assert error.message in args[1]


def test_handle_infrastructure_error(self):
    """Test handling infrastructure errors."""
    cause = Exception("Root cause")
    error = InfrastructureError("Test infrastructure error", {"field": "value"}, cause)
    context = {"operation": "test"}

    with patch("src.infrastructure.error_handler.logger") as mock_logger:
        ErrorHandler.handle_infrastructure_error(error, context)

        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        assert "Infrastructure error occurred" in args[0]
        assert error.message in args[1]


def test_handle_unexpected_error(self):
    """Test handling unexpected errors."""
    error = ValueError("Unexpected error")
    context = {"operation": "test"}

    with patch("src.infrastructure.error_handler.logger") as mock_logger:
        ErrorHandler.handle_unexpected_error(error, context)

        mock_logger.exception.assert_called_once()
        args, kwargs = mock_logger.exception.call_args
        assert "Unexpected error occurred" in args[0]
        assert str(error) in args[1]


def test_with_error_handling_success(self):
    """Test successful operation with error handling."""

    def successful_operation():
        return "success"

    result = ErrorHandler.with_error_handling(successful_operation)

    assert result == "success"


def test_with_error_handling_domain_error_reraise(self):
    """Test error handling with domain error and reraise."""

    def failing_operation():
        raise DomainError("Test error")

    with patch("src.infrastructure.error_handler.logger"):
        with pytest.raises(DomainError):
            ErrorHandler.with_error_handling(failing_operation, reraise=True)


def test_with_error_handling_domain_error_no_reraise(self):
    """Test error handling with domain error without reraise."""

    def failing_operation():
        raise DomainError("Test error")

    with patch("src.infrastructure.error_handler.logger"):
        result = ErrorHandler.with_error_handling(failing_operation, fallback_value="fallback", reraise=False)

    assert result == "fallback"


def test_with_error_handling_application_error(self):
    """Test error handling with application error."""

    def failing_operation():
        raise ApplicationError("Test error")

    with patch("src.infrastructure.error_handler.logger"):
        with pytest.raises(ApplicationError):
            ErrorHandler.with_error_handling(failing_operation)


def test_with_error_handling_infrastructure_error(self):
    """Test error handling with infrastructure error."""

    def failing_operation():
        raise InfrastructureError("Test error")

    with patch("src.infrastructure.error_handler.logger"):
        with pytest.raises(InfrastructureError):
            ErrorHandler.with_error_handling(failing_operation)


def test_with_error_handling_unexpected_error(self):
    """Test error handling with unexpected error."""

    def failing_operation():
        raise ValueError("Unexpected error")

    with patch("src.infrastructure.error_handler.logger"):
        with pytest.raises(ValueError):
            ErrorHandler.with_error_handling(failing_operation)


def test_create_error_context_minimal(self):
    """Test creating error context with minimal information."""
    context = ErrorHandler.create_error_context("test_operation")

    assert context["operation"] == "test_operation"
    assert "timestamp" in context


def test_create_error_context_full(self):
    """Test creating error context with full information."""
    context = ErrorHandler.create_error_context(
        "test_operation",
        component="TestComponent",
        user_id="user123",
        request_id="req456",
        custom_field="custom_value",
    )

    assert context["operation"] == "test_operation"
    assert context["component"] == "TestComponent"
    assert context["user_id"] == "user123"
    assert context["request_id"] == "req456"
    assert context["custom_field"] == "custom_value"
    assert "timestamp" in context


def test_with_retry_success_first_attempt(self):
    """Test successful operation on first attempt."""

    def successful_operation():
        return "success"

    result = RetryHandler.with_retry(successful_operation)

    assert result == "success"


def test_with_retry_success_after_failures(self):
    """Test successful operation after some failures."""
    call_count = 0

    def flaky_operation():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Temporary failure")
        return "success"

    with patch("src.infrastructure.error_handler.logger"):
        result = RetryHandler.with_retry(flaky_operation, max_attempts=3)

    assert result == "success"
    assert call_count == 3


def test_with_retry_all_attempts_fail(self):
    """Test operation that fails all retry attempts."""

    def always_failing_operation():
        raise ValueError("Persistent failure")

    with patch("src.infrastructure.error_handler.logger"):
        with pytest.raises(ValueError) as exc_info:
            RetryHandler.with_retry(always_failing_operation, max_attempts=3)

    assert "Persistent failure" in str(exc_info.value)


def test_with_retry_non_retryable_exception(self):
    """Test operation that raises non-retryable exception."""

    def operation_with_non_retryable_error():
        raise TypeError("Non-retryable error")

    with pytest.raises(TypeError):
        RetryHandler.with_retry(operation_with_non_retryable_error, max_attempts=3, retry_exceptions=(ValueError,))


def test_with_retry_custom_retry_exceptions(self):
    """Test retry with custom exception types."""
    call_count = 0

    def operation_with_custom_exception():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("Connection failed")
        return "success"

    with patch("src.infrastructure.error_handler.logger"):
        result = RetryHandler.with_retry(
            operation_with_custom_exception, max_attempts=3, retry_exceptions=(ConnectionError,)
        )

    assert result == "success"
    assert call_count == 2


def test_with_retry_logging(self):
    """Test that retry attempts are logged appropriately."""
    call_count = 0

    def flaky_operation():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError(f"Failure {call_count}")
        return "success"

    with patch("src.infrastructure.error_handler.logger") as mock_logger:
        RetryHandler.with_retry(flaky_operation, max_attempts=3)

        # Should log warnings for retry attempts
        assert mock_logger.warning.call_count == 2


def test_with_retry_context_logging(self):
    """Test that context is included in retry logging."""

    def failing_operation():
        raise ValueError("Test failure")

    context = {"operation": "test", "component": "TestComponent"}

    with patch("src.infrastructure.error_handler.logger") as mock_logger:
        with pytest.raises(ValueError):
            RetryHandler.with_retry(failing_operation, max_attempts=2, context=context)

        # Check that context was included in log calls
        for call in mock_logger.warning.call_args_list + mock_logger.error.call_args_list:
            if "extra" in call.kwargs:
                assert call.kwargs["extra"]["context"] == context
