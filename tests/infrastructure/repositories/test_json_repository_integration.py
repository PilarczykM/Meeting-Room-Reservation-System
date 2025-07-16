"""Integration tests for JSON repository end-to-end persistence."""

import os
import tempfile
import threading
import time

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.entities.timeslot import TimeSlot
from src.infrastructure.config.models import ApplicationConfig
from src.infrastructure.container import ServiceContainer
from src.infrastructure.repositories.json_repository import JsonMeetingRoomRepository
from src.infrastructure.service_configurator import ServiceConfigurator


class TestJsonRepositoryIntegration:
    """Integration tests for JSON repository persistence."""

    def test_end_to_end_persistence_across_repository_instances(self):
        """Test that data persists across different repository instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first repository instance and save data
            repo1 = JsonMeetingRoomRepository(temp_dir)
            meeting_room = MeetingRoom(id="integration-room-1", capacity=15)

            # Add a booking
            time_slot = TimeSlot.create("2024-02-01T10:00:00", "2024-02-01T11:00:00")
            booking = meeting_room.book(time_slot, "Integration Test User", 8)

            repo1.save(meeting_room)

            # Create second repository instance (simulating app restart)
            repo2 = JsonMeetingRoomRepository(temp_dir)

            # Verify data persisted
            loaded_room = repo2.find_by_id("integration-room-1")
            assert loaded_room is not None
            assert loaded_room.id == "integration-room-1"
            assert loaded_room.capacity == 15
            assert len(loaded_room.bookings) == 1
            assert loaded_room.bookings[0].booker == "Integration Test User"
            assert loaded_room.bookings[0].attendees == 8
            assert loaded_room.bookings[0].booking_id == booking.booking_id

    def test_multiple_meeting_rooms_persistence(self):
        """Test persistence of multiple meeting rooms."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonMeetingRoomRepository(temp_dir)

            # Create multiple meeting rooms with different configurations
            rooms = []
            for i in range(3):
                room = MeetingRoom(id=f"multi-room-{i}", capacity=10 + i * 5)

                # Add different numbers of bookings to each room
                for j in range(i + 1):
                    time_slot = TimeSlot.create(
                        f"2024-02-{j + 1:02d}T{10 + j}:00:00", f"2024-02-{j + 1:02d}T{11 + j}:00:00"
                    )
                    room.book(time_slot, f"User {j}", 4 + j)

                rooms.append(room)
                repo.save(room)

            # Create new repository instance
            repo2 = JsonMeetingRoomRepository(temp_dir)

            # Verify all rooms persisted correctly
            all_rooms = repo2.find_all()
            assert len(all_rooms) == 3

            room_ids = {room.id for room in all_rooms}
            assert room_ids == {"multi-room-0", "multi-room-1", "multi-room-2"}

            # Verify specific room details
            for i, original_room in enumerate(rooms):
                loaded_room = repo2.find_by_id(f"multi-room-{i}")
                assert loaded_room is not None
                assert loaded_room.capacity == original_room.capacity
                assert len(loaded_room.bookings) == len(original_room.bookings)

    def test_concurrent_access_thread_safety(self):
        """Test that concurrent access maintains data integrity."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonMeetingRoomRepository(temp_dir)
            results = []
            errors = []

            def create_and_save_room(room_id: str):
                try:
                    room = MeetingRoom(id=room_id, capacity=20)
                    time_slot = TimeSlot.create("2024-02-15T14:00:00", "2024-02-15T15:00:00")
                    booking = room.book(time_slot, f"Concurrent User {room_id}", 6)
                    repo.save(room)
                    results.append((room_id, booking.booking_id))
                except Exception as e:
                    errors.append((room_id, str(e)))

            # Create multiple threads that save rooms concurrently
            threads = []
            for i in range(5):
                thread = threading.Thread(target=create_and_save_room, args=[f"concurrent-room-{i}"])
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify no errors occurred
            assert len(errors) == 0, f"Errors occurred: {errors}"
            assert len(results) == 5

            # Verify all rooms were saved correctly
            all_rooms = repo.find_all()
            assert len(all_rooms) == 5

            for room_id, booking_id in results:
                room = repo.find_by_id(room_id)
                assert room is not None
                assert len(room.bookings) == 1
                assert room.bookings[0].booking_id == booking_id

    def test_configuration_integration(self):
        """Test that JSON repository works with configuration system."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create configuration with JSON storage
            config = ApplicationConfig(storage={"type": "json", "path": temp_dir})

            # Set up dependency injection
            container = ServiceContainer()
            configurator = ServiceConfigurator(container, config)
            configurator.configure_repositories()

            # Resolve repository from container
            from src.domain.repositories.meeting_room_repository import MeetingRoomRepository

            repository = container.resolve(MeetingRoomRepository)

            # Verify it's the JSON repository wrapper
            assert hasattr(repository, "_repository")
            assert isinstance(repository._repository, JsonMeetingRoomRepository)
            assert repository._repository._storage_path == temp_dir

            # Test actual functionality
            meeting_room = MeetingRoom(id="config-test-room", capacity=12)
            time_slot = TimeSlot.create("2024-02-20T09:00:00", "2024-02-20T10:00:00")
            booking = meeting_room.book(time_slot, "Config Test User", 5)

            repository.save(meeting_room)

            # Verify persistence by creating new container
            container2 = ServiceContainer()
            configurator2 = ServiceConfigurator(container2, config)
            configurator2.configure_repositories()

            repository2 = container2.resolve(MeetingRoomRepository)
            loaded_room = repository2.find_by_id("config-test-room")

            assert loaded_room is not None
            assert loaded_room.capacity == 12
            assert len(loaded_room.bookings) == 1
            assert loaded_room.bookings[0].booking_id == booking.booking_id

    def test_large_dataset_performance(self):
        """Test repository performance with larger datasets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonMeetingRoomRepository(temp_dir)

            # Create a room with many bookings
            room = MeetingRoom(id="performance-room", capacity=20)

            # Add 50 bookings
            bookings = []
            for i in range(50):
                time_slot = TimeSlot.create(
                    f"2024-03-{(i % 28) + 1:02d}T{(i % 12) + 8:02d}:00:00",
                    f"2024-03-{(i % 28) + 1:02d}T{(i % 12) + 9:02d}:00:00",
                )
                booking = room.book(time_slot, f"Performance User {i}", 4 + (i % 16))
                bookings.append(booking)

            # Measure save time
            start_time = time.time()
            repo.save(room)
            save_time = time.time() - start_time

            # Measure load time
            start_time = time.time()
            loaded_room = repo.find_by_id("performance-room")
            load_time = time.time() - start_time

            # Verify correctness
            assert loaded_room is not None
            assert len(loaded_room.bookings) == 50

            # Verify reasonable performance (should be under 1 second each)
            assert save_time < 1.0, f"Save took too long: {save_time:.3f}s"
            assert load_time < 1.0, f"Load took too long: {load_time:.3f}s"

            # Verify all bookings are correct
            loaded_booking_ids = {b.booking_id for b in loaded_room.bookings}
            original_booking_ids = {b.booking_id for b in bookings}
            assert loaded_booking_ids == original_booking_ids

    def test_crud_operations_integration(self):
        """Test all CRUD operations work together end-to-end."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonMeetingRoomRepository(temp_dir)

            # CREATE: Create and save multiple rooms
            room1 = MeetingRoom(id="crud-room-1", capacity=10)
            room2 = MeetingRoom(id="crud-room-2", capacity=15)
            room3 = MeetingRoom(id="crud-room-3", capacity=20)

            repo.save(room1)
            repo.save(room2)
            repo.save(room3)

            # READ: Verify all rooms exist
            all_rooms = repo.find_all()
            assert len(all_rooms) == 3

            found_room = repo.find_by_id("crud-room-2")
            assert found_room is not None
            assert found_room.capacity == 15

            # UPDATE: Modify a room and save
            time_slot = TimeSlot.create("2024-04-01T10:00:00", "2024-04-01T11:00:00")
            found_room.book(time_slot, "CRUD Test User", 8)
            repo.save(found_room)

            # Verify update persisted
            updated_room = repo.find_by_id("crud-room-2")
            assert len(updated_room.bookings) == 1
            assert updated_room.bookings[0].booker == "CRUD Test User"

            # DELETE: Remove a room
            repo.delete("crud-room-1")

            # Verify deletion
            deleted_room = repo.find_by_id("crud-room-1")
            assert deleted_room is None

            remaining_rooms = repo.find_all()
            assert len(remaining_rooms) == 2

            room_ids = {room.id for room in remaining_rooms}
            assert room_ids == {"crud-room-2", "crud-room-3"}

    def test_file_system_integration(self):
        """Test that JSON files are created correctly on the file system."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonMeetingRoomRepository(temp_dir)

            # Create and save a room
            room = MeetingRoom(id="filesystem-room", capacity=18)
            time_slot = TimeSlot.create("2024-05-01T14:00:00", "2024-05-01T15:00:00")
            room.book(time_slot, "Filesystem User", 7)

            repo.save(room)

            # Verify JSON file was created
            expected_file = os.path.join(temp_dir, "filesystem-room.json")
            assert os.path.exists(expected_file)

            # Verify file contents
            import json

            with open(expected_file) as f:
                data = json.load(f)

            assert data["id"] == "filesystem-room"
            assert data["capacity"] == 18
            assert len(data["bookings"]) == 1
            assert data["bookings"][0]["booker"] == "Filesystem User"
            assert data["bookings"][0]["attendees"] == 7

            # Verify file is properly formatted JSON
            assert isinstance(data, dict)
            assert "id" in data
            assert "capacity" in data
            assert "bookings" in data
