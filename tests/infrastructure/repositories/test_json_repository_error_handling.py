"""Tests for JSON-based meeting room repository."""

import json
import os
import tempfile
import threading
import time
from unittest.mock import mock_open, patch

import pytest

from src.domain.aggregates.meeting_room import MeetingRoom
from src.infrastructure.exceptions import StorageError
from src.infrastructure.repositories.json_repository import JsonMeetingRoomRepository


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
