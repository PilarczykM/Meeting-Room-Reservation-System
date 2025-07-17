from unittest.mock import MagicMock

import pytest

from src.application.services.query_service import QueryService
from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.entities.booking import Booking
from src.domain.entities.timeslot import TimeSlot


@pytest.fixture
def query_service():
    booking_repository = MagicMock()
    return QueryService(booking_repository)


def test_get_all_bookings_returns_empty_list_when_no_bookings(query_service):
    # Arrange
    query_service.booking_repository.find_all.return_value = []

    # Act
    bookings = query_service.get_all_bookings()

    # Assert
    assert bookings == []
    query_service.booking_repository.find_all.assert_called_once()


def test_get_all_bookings_returns_formatted_bookings(query_service):
    # Arrange
    time_slot1 = TimeSlot.create("2025-07-15T10:00:00", "2025-07-15T11:00:00")
    booking1 = Booking.create(time_slot1, "booker1", 10, booking_id="id1")

    time_slot2 = TimeSlot.create("2025-07-15T12:00:00", "2025-07-15T13:00:00")
    booking2 = Booking.create(time_slot2, "booker2", 5, booking_id="id2")

    # Create a meeting room with bookings
    meeting_room = MeetingRoom(room_id="main-room")
    meeting_room.bookings = [booking1, booking2]

    query_service.booking_repository.find_all.return_value = [meeting_room]

    expected_bookings = [
        {
            "booking_id": "id1",
            "start_time": "2025-07-15T10:00:00+00:00",
            "end_time": "2025-07-15T11:00:00+00:00",
            "booker": "booker1",
            "attendees": 10,
        },
        {
            "booking_id": "id2",
            "start_time": "2025-07-15T12:00:00+00:00",
            "end_time": "2025-07-15T13:00:00+00:00",
            "booker": "booker2",
            "attendees": 5,
        },
    ]

    # Act
    bookings = query_service.get_all_bookings()

    # Assert
    assert bookings == expected_bookings
    query_service.booking_repository.find_all.assert_called_once()
