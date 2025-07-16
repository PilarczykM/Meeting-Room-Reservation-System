"""Tests for JSON-based meeting room repository."""

import os
import tempfile

import pytest

from src.domain.repositories.meeting_room_repository import MeetingRoomRepository
from src.infrastructure.exceptions import StorageConfigurationError
from src.infrastructure.repositories.json_repository import JsonMeetingRoomRepository


class TestJsonMeetingRoomRepositoryInitialization:
    """Test cases for JsonMeetingRoomRepository initialization."""

    def test_repository_implements_interface(self):
        """Test that JsonMeetingRoomRepository implements MeetingRoomRepository interface."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            assert isinstance(repository, MeetingRoomRepository)

    def test_repository_initialization_with_default_path(self):
        """Test repository initialization with default storage path."""
        repository = JsonMeetingRoomRepository()
        assert repository._storage_path == "data/meeting_rooms"

    def test_repository_initialization_with_custom_path(self):
        """Test repository initialization with custom storage path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = os.path.join(temp_dir, "custom_storage")
            repository = JsonMeetingRoomRepository(custom_path)
            assert repository._storage_path == custom_path

    def test_repository_creates_storage_directory(self):
        """Test that repository creates storage directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = os.path.join(temp_dir, "new_storage_dir")
            assert not os.path.exists(storage_path)

            JsonMeetingRoomRepository(storage_path)

            assert os.path.exists(storage_path)
            assert os.path.isdir(storage_path)

    def test_repository_handles_existing_directory(self):
        """Test that repository works with existing storage directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Directory already exists
            repository = JsonMeetingRoomRepository(temp_dir)
            assert repository._storage_path == temp_dir

    def test_repository_raises_error_for_invalid_path(self):
        """Test that repository raises error for invalid storage path."""
        # Try to create directory in a location that doesn't allow it
        invalid_path = "/root/invalid_storage_path"

        with pytest.raises(StorageConfigurationError):
            JsonMeetingRoomRepository(invalid_path)

    def test_repository_has_thread_lock(self):
        """Test that repository has thread synchronization lock."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            assert hasattr(repository, "_lock")
            # Should be a threading lock

            # Should be a threading lock - check if it has acquire/release methods
            assert hasattr(repository._lock, "acquire")
            assert hasattr(repository._lock, "release")

    def test_repository_initializes_empty_cache(self):
        """Test that repository initializes with empty in-memory cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            assert hasattr(repository, "_cache")
            assert repository._cache == {}
