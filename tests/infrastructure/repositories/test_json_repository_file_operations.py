"""Tests for JSON-based meeting room repository."""

import os
import tempfile

from src.infrastructure.repositories.json_repository import JsonMeetingRoomRepository


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
