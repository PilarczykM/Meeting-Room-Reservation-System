import pytest

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository


# Dummy concrete implementation for testing purposes
class ConcreteMeetingRoomRepository(MeetingRoomRepository):
    def save(self, meeting_room: MeetingRoom) -> None:
        pass

    def find_by_id(self, room_id: str) -> MeetingRoom | None:
        return None

    def find_all(self) -> list[MeetingRoom]:
        return []

    def delete(self, room_id: str) -> None:
        pass


def test_abstract_methods_exist():
    # Ensure that the abstract methods are defined in the interface
    assert "save" in MeetingRoomRepository.__abstractmethods__
    assert "find_by_id" in MeetingRoomRepository.__abstractmethods__
    assert "find_all" in MeetingRoomRepository.__abstractmethods__
    assert "delete" in MeetingRoomRepository.__abstractmethods__


def test_concrete_implementation_must_implement_all_abstract_methods():
    # This test ensures that a concrete implementation cannot be instantiated
    # unless all abstract methods are implemented.
    # If any abstract method is not implemented, a TypeError will be raised.
    try:
        ConcreteMeetingRoomRepository()
    except TypeError:
        pytest.fail("ConcreteMeetingRoomRepository did not implement all abstract methods")


def test_concrete_implementation_can_be_instantiated():
    # This test ensures that our dummy concrete implementation can be instantiated
    # which implies it has implemented all abstract methods.
    repo = ConcreteMeetingRoomRepository()
    assert isinstance(repo, MeetingRoomRepository)
