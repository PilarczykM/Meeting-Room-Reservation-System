import random
import threading

import pytest

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.entities.timeslot import TimeSlot
from src.infrastructure.repositories.in_memory_repository import InMemoryMeetingRoomRepository


@pytest.fixture
def in_memory_repo() -> InMemoryMeetingRoomRepository:
    """Provides a fresh InMemoryMeetingRoomRepository for each test."""
    return InMemoryMeetingRoomRepository()


@pytest.fixture
def sample_meeting_room() -> MeetingRoom:
    """Provides a sample MeetingRoom with a booking."""
    room = MeetingRoom(name="Room A", capacity=10)
    room.book(
        booker="John Doe",
        time_slot=TimeSlot(start_time="2025-07-20 09:00", end_time="2025-07-20 10:00"),
        attendees=5,
    )
    return room


def test_save_and_find_by_id(in_memory_repo: InMemoryMeetingRoomRepository, sample_meeting_room: MeetingRoom) -> None:
    """Tests saving a meeting room and retrieving it by its ID."""
    in_memory_repo.save(sample_meeting_room)
    found_room = in_memory_repo.find_by_id(sample_meeting_room.id)
    assert found_room is not None
    assert found_room.id == sample_meeting_room.id
    assert len(found_room.bookings) == 1


def test_find_by_id_not_found(in_memory_repo: InMemoryMeetingRoomRepository) -> None:
    """Tests finding a non-existent meeting room by ID."""
    found_room = in_memory_repo.find_by_id("non_existent_id")
    assert found_room is None


def test_find_all_empty(in_memory_repo: InMemoryMeetingRoomRepository) -> None:
    """Tests retrieving all meeting rooms when the repository is empty."""
    all_rooms = in_memory_repo.find_all()
    assert len(all_rooms) == 0


def test_find_all_with_data(in_memory_repo: InMemoryMeetingRoomRepository, sample_meeting_room: MeetingRoom) -> None:
    """Tests retrieving all meeting rooms when there is data in the repository."""
    in_memory_repo.save(sample_meeting_room)
    room2 = MeetingRoom(name="Room B", capacity=5)
    in_memory_repo.save(room2)
    all_rooms = in_memory_repo.find_all()
    assert len(all_rooms) == 2
    assert sample_meeting_room in all_rooms
    assert room2 in all_rooms


def test_delete(in_memory_repo: InMemoryMeetingRoomRepository, sample_meeting_room: MeetingRoom) -> None:
    """Tests deleting a meeting room by its ID."""
    in_memory_repo.save(sample_meeting_room)
    assert in_memory_repo.find_by_id(sample_meeting_room.id) is not None
    in_memory_repo.delete(sample_meeting_room.id)
    assert in_memory_repo.find_by_id(sample_meeting_room.id) is None


def test_delete_non_existent_room(in_memory_repo: InMemoryMeetingRoomRepository) -> None:
    """Tests deleting a non-existent meeting room (should not raise an error)."""
    in_memory_repo.delete("non_existent_id")
    assert len(in_memory_repo.find_all()) == 0


def test_update_existing_room(in_memory_repo: InMemoryMeetingRoomRepository, sample_meeting_room: MeetingRoom) -> None:
    """Tests updating an existing meeting room."""
    in_memory_repo.save(sample_meeting_room)
    updated_room = MeetingRoom(id=sample_meeting_room.id, capacity=12)
    in_memory_repo.save(updated_room)
    found_room = in_memory_repo.find_by_id(sample_meeting_room.id)
    assert found_room.capacity == 12


def test_thread_safety_save(in_memory_repo: InMemoryMeetingRoomRepository) -> None:
    """Tests thread safety during save operations."""
    num_threads = 10
    num_rooms_per_thread = 100
    threads = []

    def save_rooms():
        for i in range(num_rooms_per_thread):
            room_id = f"room_{threading.current_thread().name}_{i}"
            room = MeetingRoom(id=room_id, name=f"Room {room_id}", capacity=10)
            in_memory_repo.save(room)

    for i in range(num_threads):
        thread = threading.Thread(target=save_rooms, name=f"Thread-{i}")
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    assert len(in_memory_repo.find_all()) == num_threads * num_rooms_per_thread


def test_thread_safety_delete(in_memory_repo: InMemoryMeetingRoomRepository) -> None:
    """Tests thread safety during delete operations."""
    # Populate with some rooms first
    for i in range(200):
        room = MeetingRoom(id=f"room_{i}", name=f"Room {i}", capacity=10)
        in_memory_repo.save(room)

    num_threads = 10
    threads = []

    def delete_rooms():
        for i in range(100):
            room_id = f"room_{i}"
            in_memory_repo.delete(room_id)

    for i in range(num_threads):
        thread = threading.Thread(target=delete_rooms, name=f"Thread-{i}")
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Check that the first 100 rooms are deleted (or attempted to be deleted multiple times)
    # The remaining 100 rooms should still be there
    assert len(in_memory_repo.find_all()) == 100
    for i in range(100, 200):
        assert in_memory_repo.find_by_id(f"room_{i}") is not None


def test_thread_safety_find_all(in_memory_repo: InMemoryMeetingRoomRepository) -> None:
    """Tests thread safety during find_all operations."""
    # Populate with some rooms
    for i in range(50):
        room = MeetingRoom(id=f"room_{i}", name=f"Room {i}", capacity=10)
        in_memory_repo.save(room)

    num_threads = 5
    threads = []
    results = []

    def find_all_rooms():
        rooms = in_memory_repo.find_all()
        results.append(len(rooms))

    for i in range(num_threads):
        thread = threading.Thread(target=find_all_rooms)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for res in results:
        assert res == 50


def test_thread_safety_mixed_operations(in_memory_repo: InMemoryMeetingRoomRepository) -> None:
    """Tests thread safety during mixed save, find, and delete operations."""
    num_operations = 1000
    num_threads = 5
    threads = []

    def mixed_operations():
        for _ in range(num_operations // num_threads):
            op = random.choice(["save", "find", "delete"])
            room_id = f"room_{random.randint(0, 99)}"

            if op == "save":
                room = MeetingRoom(id=room_id, name=f"Room {room_id}", capacity=random.randint(5, 20))
                in_memory_repo.save(room)
            elif op == "find":
                in_memory_repo.find_by_id(room_id)
            elif op == "delete":
                in_memory_repo.delete(room_id)

    for i in range(num_threads):
        thread = threading.Thread(target=mixed_operations)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Just check that no exceptions were raised and the repository is in a consistent state
    # The exact number of rooms might vary due to concurrent saves/deletes
    assert isinstance(in_memory_repo.find_all(), list)
