"""Tests for infrastructure exceptions."""

import argparse

from src.infrastructure.exceptions import (
    CLIError,
    CommandParsingError,
    DataPersistenceError,
    InfrastructureError,
    RepositoryError,
    ResourceCleanupError,
    ServiceConfigurationError,
)


def test_infrastructure_error_basic(self):
    """Test basic infrastructure error creation."""
    error = InfrastructureError("Test error")

    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.details == {}
    assert error.cause is None


def test_infrastructure_error_with_details(self):
    """Test infrastructure error with details."""
    details = {"component": "test", "operation": "test_op"}
    error = InfrastructureError("Test error", details)

    assert error.message == "Test error"
    assert error.details == details
    assert "Details:" in str(error)


def test_infrastructure_error_with_cause(self):
    """Test infrastructure error with cause."""
    cause = ValueError("Root cause")
    error = InfrastructureError("Test error", cause=cause)

    assert error.message == "Test error"
    assert error.cause is cause


def test_infrastructure_error_full(self):
    """Test infrastructure error with all parameters."""
    details = {"key": "value"}
    cause = Exception("Root cause")
    error = InfrastructureError("Test error", details, cause)

    assert error.message == "Test error"
    assert error.details == details
    assert error.cause is cause


def test_repository_error_basic(self):
    """Test basic repository error creation."""
    error = RepositoryError("save")

    assert "Repository save failed" in str(error)
    assert error.details["operation"] == "save"


def test_repository_error_with_entity_type(self):
    """Test repository error with entity type."""
    error = RepositoryError("delete", entity_type="Booking")

    assert "Repository delete failed for Booking" in str(error)
    assert error.details["entity_type"] == "Booking"


def test_repository_error_with_entity_id(self):
    """Test repository error with entity ID."""
    error = RepositoryError("find", entity_type="Booking", entity_id="123")

    assert "Repository find failed for Booking (ID: 123)" in str(error)
    assert error.details["entity_id"] == "123"


def test_repository_error_with_cause(self):
    """Test repository error with cause."""
    cause = ConnectionError("Database connection failed")
    error = RepositoryError("save", cause=cause)

    assert error.cause is cause


def test_data_persistence_error_basic(self):
    """Test basic data persistence error creation."""
    error = DataPersistenceError("write")

    assert "Data persistence failed: write" in str(error)
    assert error.details["operation"] == "write"


def test_data_persistence_error_with_data_type(self):
    """Test data persistence error with data type."""
    error = DataPersistenceError("serialize", data_type="Booking")

    assert error.details["data_type"] == "Booking"


def test_data_persistence_error_with_cause(self):
    """Test data persistence error with cause."""
    cause = OSError("Disk full")
    error = DataPersistenceError("write", cause=cause)

    assert error.cause is cause


def test_cli_error_basic(self):
    """Test basic CLI error creation."""
    error = CLIError("book")

    assert "CLI command failed: book" in str(error)
    assert error.details["command"] == "book"


def test_cli_error_with_args(self):
    """Test CLI error with arguments."""
    args = ["--room", "A", "--time", "10:00"]
    error = CLIError("book", args)

    assert error.details["args"] == args


def test_cli_error_with_cause(self):
    """Test CLI error with cause."""
    cause = ValueError("Invalid argument")
    error = CLIError("book", cause=cause)

    assert error.cause is cause


def test_command_parsing_error_basic(self):
    """Test basic command parsing error creation."""
    error = CommandParsingError("book")

    assert "Failed to parse command: book" in str(error)
    assert error.details["command"] == "book"


def test_command_parsing_error_with_invalid_args(self):
    """Test command parsing error with invalid arguments."""
    invalid_args = ["--invalid-flag", "bad-value"]
    error = CommandParsingError("book", invalid_args)

    assert "Invalid arguments:" in str(error)
    assert error.details["invalid_args"] == invalid_args


def test_command_parsing_error_with_cause(self):
    """Test command parsing error with cause."""
    cause = argparse.ArgumentError(None, "Invalid argument")
    error = CommandParsingError("book", cause=cause)

    assert error.cause is cause


def test_service_configuration_error_basic(self):
    """Test basic service configuration error creation."""
    error = ServiceConfigurationError("BookingService")

    assert "Service configuration failed: BookingService" in str(error)
    assert error.details["service_name"] == "BookingService"


def test_service_configuration_error_with_step(self):
    """Test service configuration error with configuration step."""
    error = ServiceConfigurationError("BookingService", "dependency_injection")

    assert "at step: dependency_injection" in str(error)
    assert error.details["configuration_step"] == "dependency_injection"


def test_service_configuration_error_with_cause(self):
    """Test service configuration error with cause."""
    cause = ImportError("Module not found")
    error = ServiceConfigurationError("BookingService", cause=cause)

    assert error.cause is cause


def test_resource_cleanup_error_basic(self):
    """Test basic resource cleanup error creation."""
    error = ResourceCleanupError("database_connection")

    assert "Failed to cleanup resource: database_connection" in str(error)
    assert error.details["resource_type"] == "database_connection"


def test_resource_cleanup_error_with_id(self):
    """Test resource cleanup error with resource ID."""
    error = ResourceCleanupError("file_handle", "handle_123")

    assert "(ID: handle_123)" in str(error)
    assert error.details["resource_id"] == "handle_123"


def test_resource_cleanup_error_with_cause(self):
    """Test resource cleanup error with cause."""
    cause = OSError("Permission denied")
    error = ResourceCleanupError("file_handle", cause=cause)

    assert error.cause is cause
