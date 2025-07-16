"""Tests for JSON-based meeting room repository."""

import json
import os
import tempfile
import threading
import time
from unittest.mock import mock_open, patch

import pytest

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.entities.timeslot import TimeSlot
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository
from src.infrastructure.exceptions import StorageConfigurationError, StorageError
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


class TestJsonMeetingRoomRepositoryCRUD:
    """Test cases for JSON repository CRUD operations."""

    def test_save_creates_new_meeting_room_file(self):
        """Test that save() creates a new JSON file for a meeting room."""

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            meeting_room = MeetingRoom(id="new-room-1", capacity=25)

            repository.save(meeting_room)

            # Verify file was created
            file_path = repository._get_file_path("new-room-1")
            assert os.path.exists(file_path)

            # Verify cache was updated
            assert "new-room-1" in repository._cache
            assert repository._cache["new-room-1"].id == "new-room-1"

    def test_save_updates_existing_meeting_room_file(self):
        """Test that save() updates an existing meeting room file."""

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create and save initial room
            meeting_room = MeetingRoom(id="update-room-1", capacity=20)
            repository.save(meeting_room)

            # Add a booking and save again
            time_slot = TimeSlot.create("2024-01-20T09:00:00", "2024-01-20T10:00:00")
            meeting_room.book(time_slot, "Alice Johnson", 6)
            repository.save(meeting_room)

            # Verify the file was updated
            loaded_room = repository._load_from_file("update-room-1")
            assert loaded_room is not None
            assert len(loaded_room.bookings) == 1
            assert loaded_room.bookings[0].booker == "Alice Johnson"

    def test_save_is_thread_safe(self):
        """Test that save() operations are thread-safe."""

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            results = []

            def save_room(room_id: str):
                room = MeetingRoom(id=room_id, capacity=15)
                repository.save(room)
                results.append(room_id)

            # Create multiple threads saving different rooms
            threads = []
            for i in range(5):
                thread = threading.Thread(target=save_room, args=[f"thread-room-{i}"])
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify all rooms were saved
            assert len(results) == 5
            for i in range(5):
                assert f"thread-room-{i}" in results
                assert os.path.exists(repository._get_file_path(f"thread-room-{i}"))

    def test_find_by_id_returns_existing_room(self):
        """Test that find_by_id() returns an existing meeting room."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Save a room first
            original_room = MeetingRoom(id="find-room-1", capacity=30)
            repository.save(original_room)

            # Find it
            found_room = repository.find_by_id("find-room-1")

            assert found_room is not None
            assert found_room.id == "find-room-1"
            assert found_room.capacity == 30

    def test_find_by_id_returns_none_for_nonexistent_room(self):
        """Test that find_by_id() returns None for non-existent rooms."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            result = repository.find_by_id("nonexistent-room")

            assert result is None

    def test_find_by_id_uses_cache_when_available(self):
        """Test that find_by_id() uses in-memory cache when available."""
        from unittest.mock import patch

        from src.domain.aggregates.meeting_room import MeetingRoom

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Save a room to populate cache
            room = MeetingRoom(id="cached-room-1", capacity=18)
            repository.save(room)

            # Mock _load_from_file to verify it's not called
            with patch.object(repository, "_load_from_file") as mock_load:
                found_room = repository.find_by_id("cached-room-1")

                # Should not call _load_from_file since it's in cache
                mock_load.assert_not_called()
                assert found_room is not None
                assert found_room.id == "cached-room-1"

    def test_find_by_id_loads_from_file_when_not_cached(self):
        """Test that find_by_id() loads from file when not in cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create file directly (bypass cache)
            room = MeetingRoom(id="file-room-1", capacity=22)
            repository._save_to_file(room)

            # Clear cache to force file load
            repository._cache.clear()

            found_room = repository.find_by_id("file-room-1")

            assert found_room is not None
            assert found_room.id == "file-room-1"
            assert found_room.capacity == 22
            # Should now be in cache
            assert "file-room-1" in repository._cache

    def test_find_all_returns_all_meeting_rooms(self):
        """Test that find_all() returns all stored meeting rooms."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Save multiple rooms
            room1 = MeetingRoom(id="all-room-1", capacity=10)
            room2 = MeetingRoom(id="all-room-2", capacity=15)
            room3 = MeetingRoom(id="all-room-3", capacity=20)

            repository.save(room1)
            repository.save(room2)
            repository.save(room3)

            all_rooms = repository.find_all()

            assert len(all_rooms) == 3
            room_ids = {room.id for room in all_rooms}
            assert room_ids == {"all-room-1", "all-room-2", "all-room-3"}

    def test_find_all_returns_empty_list_when_no_rooms(self):
        """Test that find_all() returns empty list when no rooms exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            all_rooms = repository.find_all()

            assert all_rooms == []

    def test_find_all_loads_rooms_from_files(self):
        """Test that find_all() loads rooms from files not in cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create files directly (bypass cache)
            room1 = MeetingRoom(id="file-all-1", capacity=12)
            room2 = MeetingRoom(id="file-all-2", capacity=16)

            repository._save_to_file(room1)
            repository._save_to_file(room2)

            # Clear cache
            repository._cache.clear()

            all_rooms = repository.find_all()

            assert len(all_rooms) == 2
            room_ids = {room.id for room in all_rooms}
            assert room_ids == {"file-all-1", "file-all-2"}

    def test_delete_removes_meeting_room_file(self):
        """Test that delete() removes the meeting room file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Save a room first
            room = MeetingRoom(id="delete-room-1", capacity=14)
            repository.save(room)

            file_path = repository._get_file_path("delete-room-1")
            assert os.path.exists(file_path)

            # Delete the room
            repository.delete("delete-room-1")

            # Verify file was removed
            assert not os.path.exists(file_path)
            # Verify cache was cleared
            assert "delete-room-1" not in repository._cache

    def test_delete_handles_nonexistent_room_gracefully(self):
        """Test that delete() handles non-existent rooms gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Should not raise an exception
            repository.delete("nonexistent-room")

    def test_delete_is_thread_safe(self):
        """Test that delete() operations are thread-safe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create multiple rooms
            for i in range(5):
                room = MeetingRoom(id=f"delete-thread-{i}", capacity=10)
                repository.save(room)

            deleted_rooms = []

            def delete_room(room_id: str):
                repository.delete(room_id)
                deleted_rooms.append(room_id)

            # Delete rooms concurrently
            threads = []
            for i in range(5):
                thread = threading.Thread(target=delete_room, args=[f"delete-thread-{i}"])
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify all rooms were deleted
            assert len(deleted_rooms) == 5
            for i in range(5):
                assert not os.path.exists(repository._get_file_path(f"delete-thread-{i}"))
                assert f"delete-thread-{i}" not in repository._cache


class TestJsonMeetingRoomRepositoryErrorHandling:
    """Test cases for comprehensive error handling and recovery."""

    def test_corrupted_json_file_recovery(self):
        """Test that corrupted JSON files are handled gracefully with backup creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create and save a valid room first
            room = MeetingRoom(id="recovery-room", capacity=15)
            repository.save(room)

            # Verify it was saved correctly
            loaded_room = repository.find_by_id("recovery-room")
            assert loaded_room is not None

            # Corrupt the JSON file
            file_path = repository._get_file_path("recovery-room")
            with open(file_path, "w") as f:
                f.write("{ corrupted json content without closing brace")

            # Try to load the corrupted file - should return None and create backup
            result = repository._load_from_file("recovery-room")
            assert result is None

            # Verify backup file was created
            backup_path = f"{file_path}.backup"
            assert os.path.exists(backup_path)

            # Verify backup contains the corrupted content
            with open(backup_path) as f:
                backup_content = f.read()
            assert "corrupted json content" in backup_content

    def test_permission_error_handling(self):
        """Test handling of permission errors during file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            room = MeetingRoom(id="permission-room", capacity=12)

            # Make directory read-only to cause permission error
            os.chmod(temp_dir, 0o444)

            try:
                with pytest.raises(StorageError) as exc_info:
                    repository.save(room)

                # Verify error details
                assert "Failed to save meeting room to file" in str(exc_info.value)
                assert "permission-room" in str(exc_info.value)
            finally:
                # Restore permissions for cleanup
                os.chmod(temp_dir, 0o755)

    def test_disk_space_error_simulation(self):
        """Test handling of disk space errors during save operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            room = MeetingRoom(id="diskspace-room", capacity=10)

            # Mock file operations to simulate disk space error
            with patch("builtins.open", mock_open()) as mock_file:
                mock_file.side_effect = OSError("No space left on device")

                with pytest.raises(StorageError) as exc_info:
                    repository.save(room)

                assert "Failed to save meeting room to file" in str(exc_info.value)

    def test_missing_directory_auto_creation(self):
        """Test that missing directories are automatically created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a nested path that doesn't exist
            nested_path = os.path.join(temp_dir, "level1", "level2", "storage")

            # Repository should create the directory structure
            repository = JsonMeetingRoomRepository(nested_path)

            # Verify directory was created
            assert os.path.exists(nested_path)
            assert os.path.isdir(nested_path)

            # Verify it works for saving files
            room = MeetingRoom(id="nested-room", capacity=8)
            repository.save(room)

            file_path = repository._get_file_path("nested-room")
            assert os.path.exists(file_path)

    def test_concurrent_file_access_error_handling(self):
        """Test handling of concurrent file access conflicts."""

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            errors = []
            successes = []

            def save_room_with_delay(room_id: str, delay: float):
                try:
                    room = MeetingRoom(id=room_id, capacity=10)
                    time.sleep(delay)  # Simulate processing time
                    repository.save(room)
                    successes.append(room_id)
                except Exception as e:
                    errors.append((room_id, str(e)))

            # Create multiple threads trying to save different rooms simultaneously
            threads = []
            for i in range(3):
                thread = threading.Thread(target=save_room_with_delay, args=[f"concurrent-room-{i}", 0.01])
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # All operations should succeed due to thread safety
            assert len(errors) == 0, f"Unexpected errors: {errors}"
            assert len(successes) == 3

            # Verify all rooms were saved
            for i in range(3):
                room = repository.find_by_id(f"concurrent-room-{i}")
                assert room is not None

    def test_invalid_json_structure_handling(self):
        """Test handling of JSON files with invalid structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create a JSON file with valid JSON but invalid structure that will cause validation error
            file_path = repository._get_file_path("invalid-structure")
            with open(file_path, "w") as f:
                # Use invalid data types that will cause Pydantic validation to fail
                json.dump({"id": 123, "capacity": "not_a_number", "bookings": "not_a_list"}, f)

            # Should return None and handle gracefully
            result = repository._load_from_file("invalid-structure")
            assert result is None

            # Verify backup was created
            backup_path = f"{file_path}.backup"
            assert os.path.exists(backup_path)

    def test_empty_file_handling(self):
        """Test handling of empty JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create an empty file
            file_path = repository._get_file_path("empty-file")
            with open(file_path, "w"):
                pass  # Create empty file

            # Should return None and handle gracefully
            result = repository._load_from_file("empty-file")
            assert result is None

            # Verify backup was created
            backup_path = f"{file_path}.backup"
            assert os.path.exists(backup_path)

    def test_network_storage_error_simulation(self):
        """Test handling of network storage errors."""

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            room = MeetingRoom(id="network-room", capacity=14)

            # Mock os.replace to simulate network error
            with patch("os.replace") as mock_replace:
                mock_replace.side_effect = OSError("Network is unreachable")

                with pytest.raises(StorageError):
                    repository.save(room)

    def test_atomic_write_failure_cleanup(self):
        """Test that temporary files are cleaned up when atomic writes fail."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            room = MeetingRoom(id="atomic-fail-room", capacity=16)

            # Mock os.replace to fail after temp file is created
            with patch("os.replace") as mock_replace:
                mock_replace.side_effect = OSError("Atomic operation failed")

                import pytest

                with pytest.raises(StorageError):
                    repository.save(room)

                # Verify temporary file was cleaned up
                temp_files = [f for f in os.listdir(temp_dir) if f.endswith(".tmp")]
                assert len(temp_files) == 0, f"Temporary files not cleaned up: {temp_files}"

    def test_logging_for_error_conditions(self):
        """Test that error conditions are properly logged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)

            # Create a corrupted file
            file_path = repository._get_file_path("log-test-room")
            with open(file_path, "w") as f:
                f.write("{ invalid json")

            # Capture log output
            with patch("builtins.print") as mock_print:
                result = repository._load_from_file("log-test-room")

                # Verify error was logged (currently using print, should be proper logging)
                assert result is None
                mock_print.assert_called()

                # Verify log message contains relevant information
                log_call = mock_print.call_args[0][0]
                assert "log-test-room" in log_call
                assert "Warning" in log_call or "Failed" in log_call
