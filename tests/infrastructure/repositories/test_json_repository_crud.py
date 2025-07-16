"""Tests for JSON-based meeting room repository."""

import os
import tempfile
import threading
from unittest.mock import patch

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.entities.timeslot import TimeSlot
from src.infrastructure.repositories.json_repository import JsonMeetingRoomRepository


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
