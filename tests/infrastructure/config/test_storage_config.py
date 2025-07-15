"""Tests for storage configuration models."""

from src.infrastructure.config.models import ApplicationConfig, StorageConfig, StorageType


class TestStorageConfig:
    """Test cases for StorageConfig model."""

    def test_storage_config_defaults(self):
        """Test StorageConfig with default values."""
        config = StorageConfig()

        assert config.type == StorageType.JSON
        assert config.path == "data/meeting_rooms"

    def test_storage_config_custom_values(self):
        """Test StorageConfig with custom values."""
        config = StorageConfig(type=StorageType.IN_MEMORY, path="/custom/path/storage")

        assert config.type == StorageType.IN_MEMORY
        assert config.path == "/custom/path/storage"

    def test_storage_config_json_type(self):
        """Test StorageConfig with JSON type."""
        config = StorageConfig(type="json", path="custom/json/path")

        assert config.type == StorageType.JSON
        assert config.path == "custom/json/path"

    def test_storage_config_in_memory_type(self):
        """Test StorageConfig with in-memory type."""
        config = StorageConfig(type="in_memory")

        assert config.type == StorageType.IN_MEMORY
        assert config.path == "data/meeting_rooms"  # Default path still set


class TestApplicationConfigWithStorage:
    """Test cases for ApplicationConfig with storage configuration."""

    def test_application_config_default_storage(self):
        """Test ApplicationConfig with default storage configuration."""
        config = ApplicationConfig()

        assert hasattr(config, "storage")
        assert config.storage.type == StorageType.JSON
        assert config.storage.path == "data/meeting_rooms"

    def test_application_config_custom_storage(self):
        """Test ApplicationConfig with custom storage configuration."""
        config = ApplicationConfig(storage={"type": "in_memory", "path": "/tmp/test_storage"})

        assert config.storage.type == StorageType.IN_MEMORY
        assert config.storage.path == "/tmp/test_storage"

    def test_application_config_storage_object(self):
        """Test ApplicationConfig with StorageConfig object."""
        storage_config = StorageConfig(type=StorageType.JSON, path="/custom/path")
        config = ApplicationConfig(storage=storage_config)

        assert config.storage.type == StorageType.JSON
        assert config.storage.path == "/custom/path"

    def test_application_config_backward_compatibility(self):
        """Test that existing repository_type still works but storage takes precedence."""
        config = ApplicationConfig(repository_type="in_memory", storage={"type": "json", "path": "test/path"})

        # Storage config should take precedence
        assert config.storage.type == StorageType.JSON
        assert config.storage.path == "test/path"
        # But repository_type should still be accessible
        assert config.repository_type == "in_memory"
