import threading

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository


class InMemoryMeetingRoomRepository(MeetingRoomRepository):
    """In-memory implementation of the MeetingRoomRepository.

    This repository stores MeetingRoom aggregates in a dictionary in memory.
    It is thread-safe for concurrent access.
    """

    def __init__(self) -> None:
        self._meeting_rooms: dict[str, MeetingRoom] = {}
        self._lock = threading.Lock()

    def save(self, meeting_room: MeetingRoom) -> None:
        """Save a MeetingRoom aggregate to the in-memory store.

        If a room with the same ID already exists, it will be updated.
        """
        with self._lock:
            self._meeting_rooms[meeting_room.id] = meeting_room

    def find_by_id(self, room_id: str) -> MeetingRoom | None:
        """Find a MeetingRoom aggregate by its ID.

        Returns the MeetingRoom if found, otherwise None.
        """
        with self._lock:
            return self._meeting_rooms.get(room_id)

    def find_all(self) -> list[MeetingRoom]:
        """Retrieve all MeetingRoom aggregates from the in-memory store.

        Returns a list of all stored MeetingRoom objects.
        """
        with self._lock:
            return list(self._meeting_rooms.values())

    def delete(self, room_id: str) -> None:
        """Delete a MeetingRoom aggregate by its ID from the in-memory store.

        If the room does not exist, no action is taken.
        """
        with self._lock:
            if room_id in self._meeting_rooms:
                del self._meeting_rooms[room_id]
