"""Tests for storage-related infrastructure exceptions."""

from src.infrastructure.exceptions import StorageConfigurationError, StorageError


class TestStorageError:
    """Test cases for StorageError exception."""

    def test_storage_error_with_message_only(self):
        """Test StorageError with just a message."""
        error = StorageError("Failed to write file")

        assert str(error) == "Failed to write file"
        assert error.message == "Failed to write file"
        assert error.details == {}
        assert error.cause is None

    def test_storage_error_with_details(self):
        """Test StorageError with additional details."""
        details = {"file_path": "/tmp/test.json", "operation": "write"}
        error = StorageError("Failed to write file", details)

        assert error.message == "Failed to write file"
        assert error.details == details
        assert "Details:" in str(error)
        assert "/tmp/test.json" in str(error)

    def test_storage_error_with_cause(self):
        """Test StorageError with underlying cause."""
        cause = PermissionError("Permission denied")
        error = StorageError("Failed to write file", cause=cause)

        assert error.message == "Failed to write file"
        assert error.cause == cause

    def test_storage_error_with_all_parameters(self):
        """Test StorageError with all parameters."""
        details = {"file_path": "/tmp/test.json"}
        cause = OSError("Disk full")
        error = StorageError("Failed to write file", details, cause)

        assert error.message == "Failed to write file"
        assert error.details == details
        assert error.cause == cause


class TestStorageConfigurationError:
    """Test cases for StorageConfigurationError exception."""

    def test_storage_configuration_error_basic(self):
        """Test StorageConfigurationError with basic parameters."""
        error = StorageConfigurationError("Invalid storage path")

        assert str(error) == "Invalid storage path"
        assert error.message == "Invalid storage path"
        assert error.details == {}

    def test_storage_configuration_error_with_details(self):
        """Test StorageConfigurationError with configuration details."""
        details = {"path": "/invalid/path", "type": "json"}
        error = StorageConfigurationError("Invalid storage configuration", details)

        assert error.message == "Invalid storage configuration"
        assert error.details == details
        assert "Details:" in str(error)

    def test_storage_configuration_error_inheritance(self):
        """Test that StorageConfigurationError inherits from StorageError."""
        error = StorageConfigurationError("Config error")

        assert isinstance(error, StorageError)
        assert isinstance(error, Exception)
