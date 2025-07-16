"""Tests for configuration file loading with storage settings."""

import json
import os

from src.infrastructure.config.manager import ConfigurationManager
from src.infrastructure.config.models import StorageType


class TestConfigurationFiles:
    """Test cases for configuration file loading."""

    def test_development_config_has_storage_settings(self):
        """Test that development config includes storage configuration."""
        config_manager = ConfigurationManager()
        config = config_manager.load_config("development")

        assert hasattr(config, "storage")
        assert config.storage.type == StorageType.JSON
        assert config.storage.path == "data/meeting_rooms"

    def test_production_config_has_storage_settings(self):
        """Test that production config includes storage configuration."""
        config_manager = ConfigurationManager()
        config = config_manager.load_config("production")

        assert hasattr(config, "storage")
        assert config.storage.type == StorageType.JSON
        assert config.storage.path == "data/meeting_rooms"

    def test_test_config_has_storage_settings(self):
        """Test that test config includes storage configuration."""
        config_manager = ConfigurationManager()
        config = config_manager.load_config("test")

        assert hasattr(config, "storage")
        assert config.storage.type == StorageType.IN_MEMORY
        # Test environment should use in-memory for faster tests

    def test_config_files_exist_and_are_valid_json(self):
        """Test that all configuration files exist and contain valid JSON."""
        config_files = ["config/development.json", "config/production.json", "config/test.json"]

        for config_file in config_files:
            assert os.path.exists(config_file), f"Configuration file {config_file} does not exist"

            with open(config_file) as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    assert False, f"Configuration file {config_file} contains invalid JSON: {e}"

    def test_config_files_have_required_storage_fields(self):
        """Test that all configuration files have the required storage fields."""
        config_files = ["config/development.json", "config/production.json", "config/test.json"]

        for config_file in config_files:
            with open(config_file) as f:
                config_data = json.load(f)

            assert "storage" in config_data, f"Configuration file {config_file} missing 'storage' field"
            assert "type" in config_data["storage"], f"Configuration file {config_file} missing 'storage.type' field"
            assert "path" in config_data["storage"], f"Configuration file {config_file} missing 'storage.path' field"
