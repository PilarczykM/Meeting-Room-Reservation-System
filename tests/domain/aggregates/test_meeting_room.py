import pytest

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.exceptions import (
    BookingNotFoundError,
    InvalidAttendeeCountError,
    OverlappingBookingError,
)


@pytest.fixture
def meeting_room():
    return MeetingRoom()


def test_meeting_room_initialization(meeting_room):
    assert isinstance(meeting_room, MeetingRoom)
    assert meeting_room.bookings == []
    assert meeting_room.ROOM_CAPACITY == 20


def test_book_room_success(meeting_room, time_slot_1):
    booking = meeting_room.book(time_slot_1, "John Doe", 10)
    assert len(meeting_room.bookings) == 1
    assert booking in meeting_room.bookings
    assert booking.booker == "John Doe"
    assert booking.attendees == 10


def test_book_room_invalid_attendee_count(meeting_room, time_slot_1):
    with pytest.raises(InvalidAttendeeCountError):
        meeting_room.book(time_slot_1, "John Doe", 3)  # Too few attendees
    with pytest.raises(InvalidAttendeeCountError):
        meeting_room.book(time_slot_1, "John Doe", 21)  # Too many attendees


def test_book_room_overlapping_booking(meeting_room, time_slot_1, overlapping_time_slot):
    meeting_room.book(time_slot_1, "John Doe", 10)
    with pytest.raises(OverlappingBookingError):
        meeting_room.book(overlapping_time_slot, "Jane Doe", 5)


def test_cancel_booking_success(meeting_room, time_slot_1):
    booking = meeting_room.book(time_slot_1, "John Doe", 10)
    meeting_room.cancel(booking.booking_id)
    assert len(meeting_room.bookings) == 0


def test_cancel_booking_not_found(meeting_room):
    with pytest.raises(BookingNotFoundError):
        meeting_room.cancel("non-existent-id")


def test_list_bookings_empty(meeting_room):
    assert meeting_room.list_bookings() == []


def test_list_bookings_multiple(meeting_room, time_slot_1, time_slot_2):
    booking1 = meeting_room.book(time_slot_1, "John Doe", 10)
    booking2 = meeting_room.book(time_slot_2, "Jane Doe", 5)
    listed_bookings = meeting_room.list_bookings()
    assert len(listed_bookings) == 2
    assert listed_bookings[0] == booking1  # Should be sorted by start_time
    assert listed_bookings[1] == booking2
