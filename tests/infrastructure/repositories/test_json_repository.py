"""Tests for JSON-based meeting room repository."""

import os
import tempfile

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

        import pytest

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


class TestJsonMeetingRoomRepositoryFileOperations:
    """Test cases for JSON repository file operations."""

    def test_get_file_path_method(self):
        """Test the _get_file_path method returns correct path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            room_id = "test-room-123"

            expected_path = os.path.join(temp_dir, f"{room_id}.json")
            actual_path = repository._get_file_path(room_id)

            assert actual_path == expected_path

    def test_ensure_storage_directory_creates_missing_dirs(self):
        """Test _ensure_storage_directory creates nested directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "level1", "level2", "storage")
            JsonMeetingRoomRepository(nested_path)

            assert os.path.exists(nested_path)
            assert os.path.isdir(nested_path)


class TestJsonMeetingRoomRepositorySerialization:
    """Test cases for JSON serialization and deserialization."""

    def test_save_to_file_creates_json_file(self):
        """Test that _save_to_file creates a JSON file with correct content."""
        from src.domain.aggregates.meeting_room import MeetingRoom

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            meeting_room = MeetingRoom(id="test-room-1", capacity=15)

            repository._save_to_file(meeting_room)

            file_path = repository._get_file_path("test-room-1")
            assert os.path.exists(file_path)

            # Verify JSON content
            import json

            with open(file_path) as f:
                data = json.load(f)

            assert data["id"] == "test-room-1"
            assert data["capacity"] == 15
            assert data["bookings"] == []

    def test_save_to_file_with_bookings(self):
        """Test that _save_to_file correctly serializes meeting room with bookings."""
        from src.domain.aggregates.meeting_room import MeetingRoom
        from src.domain.entities.timeslot import TimeSlot

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            meeting_room = MeetingRoom(id="test-room-2", capacity=20)

            # Add a booking
            time_slot = TimeSlot.create("2024-01-15T10:00:00", "2024-01-15T11:00:00")
            booking = meeting_room.book(time_slot, "John Doe", 8)

            repository._save_to_file(meeting_room)

            file_path = repository._get_file_path("test-room-2")

            # Verify JSON content includes booking
            import json

            with open(file_path) as f:
                data = json.load(f)

            assert len(data["bookings"]) == 1
            assert data["bookings"][0]["booker"] == "John Doe"
            assert data["bookings"][0]["attendees"] == 8
            assert data["bookings"][0]["booking_id"] == booking.booking_id

    def test_load_from_file_returns_meeting_room(self):
        """Test that _load_from_file correctly deserializes JSON to MeetingRoom."""
        from src.domain.aggregates.meeting_room import MeetingRoom

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create and save a meeting room first
            original_room = MeetingRoom(id="test-room-3", capacity=12)
            repository._save_to_file(original_room)

            # Load it back
            loaded_room = repository._load_from_file("test-room-3")

            assert loaded_room is not None
            assert loaded_room.id == "test-room-3"
            assert loaded_room.capacity == 12
            assert loaded_room.bookings == []

    def test_load_from_file_with_bookings(self):
        """Test that _load_from_file correctly deserializes meeting room with bookings."""
        from src.domain.aggregates.meeting_room import MeetingRoom
        from src.domain.entities.timeslot import TimeSlot

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create meeting room with booking
            original_room = MeetingRoom(id="test-room-4", capacity=18)
            time_slot = TimeSlot.create("2024-01-15T14:00:00", "2024-01-15T15:00:00")
            original_booking = original_room.book(time_slot, "Jane Smith", 10)

            repository._save_to_file(original_room)

            # Load it back
            loaded_room = repository._load_from_file("test-room-4")

            assert loaded_room is not None
            assert len(loaded_room.bookings) == 1
            assert loaded_room.bookings[0].booker == "Jane Smith"
            assert loaded_room.bookings[0].attendees == 10
            assert loaded_room.bookings[0].booking_id == original_booking.booking_id

    def test_load_from_file_nonexistent_returns_none(self):
        """Test that _load_from_file returns None for non-existent files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            result = repository._load_from_file("nonexistent-room")

            assert result is None

    def test_save_to_file_uses_atomic_writes(self):
        """Test that _save_to_file uses atomic writes with temporary files."""
        from unittest.mock import mock_open, patch

        from src.domain.aggregates.meeting_room import MeetingRoom

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            meeting_room = MeetingRoom(id="test-room-5")

            # Mock file operations to verify atomic write pattern
            with patch("builtins.open", mock_open()) as mock_file:
                with patch("os.replace") as mock_replace:
                    repository._save_to_file(meeting_room)

                    # Verify temporary file was used
                    mock_file.assert_called()
                    call_args = mock_file.call_args[0]
                    assert call_args[0].endswith(".tmp")

                    # Verify atomic move was called
                    mock_replace.assert_called_once()

    def test_save_to_file_handles_write_errors(self):
        """Test that _save_to_file handles write errors gracefully."""
        from src.domain.aggregates.meeting_room import MeetingRoom
        from src.infrastructure.exceptions import StorageError

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            meeting_room = MeetingRoom(id="test-room-6")

            # Make directory read-only to cause write error
            os.chmod(temp_dir, 0o444)

            try:
                import pytest

                with pytest.raises(StorageError):
                    repository._save_to_file(meeting_room)
            finally:
                # Restore permissions for cleanup
                os.chmod(temp_dir, 0o755)

    def test_load_from_file_handles_corrupted_json(self):
        """Test that _load_from_file handles corrupted JSON files gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create a corrupted JSON file
            file_path = repository._get_file_path("corrupted-room")
            with open(file_path, "w") as f:
                f.write("{ invalid json content")

            result = repository._load_from_file("corrupted-room")

            # Should return None and handle error gracefully
            assert result is None
