"""Tests for JSON-based meeting room repository."""

import json
import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.entities.timeslot import TimeSlot
from src.infrastructure.exceptions import StorageError
from src.infrastructure.repositories.json_repository import JsonMeetingRoomRepository


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
            with open(file_path) as f:
                data = json.load(f)

            assert data["id"] == "test-room-1"
            assert data["capacity"] == 15
            assert data["bookings"] == []

    def test_save_to_file_with_bookings(self):
        """Test that _save_to_file correctly serializes meeting room with bookings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            meeting_room = MeetingRoom(id="test-room-2", capacity=20)

            # Add a booking
            time_slot = TimeSlot.create("2024-01-15T10:00:00", "2024-01-15T11:00:00")
            booking = meeting_room.book(time_slot, "John Doe", 8)

            repository._save_to_file(meeting_room)

            file_path = repository._get_file_path("test-room-2")

            # Verify JSON content includes booking
            with open(file_path) as f:
                data = json.load(f)

            assert len(data["bookings"]) == 1
            assert data["bookings"][0]["booker"] == "John Doe"
            assert data["bookings"][0]["attendees"] == 8
            assert data["bookings"][0]["booking_id"] == booking.booking_id

    def test_load_from_file_returns_meeting_room(self):
        """Test that _load_from_file correctly deserializes JSON to MeetingRoom."""
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
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = JsonMeetingRoomRepository(temp_dir)
            meeting_room = MeetingRoom(id="test-room-6")

            # Make directory read-only to cause write error
            os.chmod(temp_dir, 0o444)

            try:
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
