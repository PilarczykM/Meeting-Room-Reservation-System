from abc import ABC, abstractmethod

from src.domain.aggregates.meeting_room import MeetingRoom


class MeetingRoomRepository(ABC):
    """Abstract base class for a Meeting Room Repository.

    Defines the contract for data access operations related to MeetingRoom aggregates.
    """

    @abstractmethod
    def save(self, meeting_room: MeetingRoom) -> None:
        """Save a MeetingRoom aggregate.

        If the meeting room already exists (identified by its ID), it should be updated.
        Otherwise, it should be created.
        """
        pass

    @abstractmethod
    def find_by_id(self, room_id: str) -> MeetingRoom | None:
        """Find a MeetingRoom aggregate by its unique identifier.

        Returns the MeetingRoom if found, otherwise returns None.
        """
        pass

    @abstractmethod
    def find_all(self) -> list[MeetingRoom]:
        """Retrieve all MeetingRoom aggregates.

        Returns a list of all MeetingRoom objects currently stored.
        """
        pass

    @abstractmethod
    def delete(self, room_id: str) -> None:
        """Delete a MeetingRoom aggregate by its unique identifier.

        If the meeting room does not exist, this method should handle it gracefully
        (e.g., by doing nothing or raising a specific exception if defined by the implementation).
        """
        pass
