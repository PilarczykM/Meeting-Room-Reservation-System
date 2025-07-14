from datetime import datetime

import pytest

from src.domain.entities.booking import Booking
from src.domain.entities.timeslot import TimeSlot
from src.domain.exceptions import InvalidAttendeeCountError


@pytest.fixture
def sample_timeslot():
    start = datetime(2024, 7, 14, 9, 0, 0)
    end = datetime(2024, 7, 14, 10, 0, 0)
    return TimeSlot(start_time=start, end_time=end)


def test_booking_creation_valid(sample_timeslot):
    booking = Booking(time_slot=sample_timeslot, booker="John Doe", attendees=10)
    assert booking.time_slot == sample_timeslot
    assert booking.booker == "John Doe"
    assert booking.attendees == 10
    assert isinstance(booking.booking_id, str)


def test_booking_id_is_frozen(sample_timeslot):
    booking = Booking(time_slot=sample_timeslot, booker="John Doe", attendees=10)
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        booking.booking_id = "new-id"


@pytest.mark.parametrize(
    "attendees, expected_exception",
    [
        (3, InvalidAttendeeCountError),  # Below min
        (21, InvalidAttendeeCountError),  # Above max
        (4, None),  # Min valid
        (20, None),  # Max valid
        (10, None),  # Mid valid
    ],
)
def test_booking_attendee_validation(sample_timeslot, attendees, expected_exception):
    if expected_exception:
        with pytest.raises(
            expected_exception,
            match="Number of attendees must be between 4 and 20 \\(inclusive\\)\\.",
        ):
            Booking(time_slot=sample_timeslot, booker="John Doe", attendees=attendees)
    else:
        booking = Booking(time_slot=sample_timeslot, booker="John Doe", attendees=attendees)
        assert booking.attendees == attendees


def test_booking_equality():
    ts = TimeSlot(
        start_time=datetime(2024, 7, 14, 9, 0),
        end_time=datetime(2024, 7, 14, 10, 0),
    )
    booking1 = Booking(time_slot=ts, booker="Jane Doe", attendees=5)
    booking2 = Booking(time_slot=ts, booker="Jane Doe", attendees=5)

    # Manually set booking_id for predictable equality testing
    object.__setattr__(booking2, "booking_id", booking1.booking_id)

    assert booking1 == booking2


def test_booking_inequality_different_id():
    ts = TimeSlot(
        start_time=datetime(2024, 7, 14, 9, 0),
        end_time=datetime(2024, 7, 14, 10, 0),
    )
    booking1 = Booking(time_slot=ts, booker="Jane Doe", attendees=5)
    booking2 = Booking(time_slot=ts, booker="Jane Doe", attendees=5)
    # booking_id will be different by default
    assert booking1 != booking2


def test_booking_hashable():
    ts = TimeSlot(
        start_time=datetime(2024, 7, 14, 9, 0),
        end_time=datetime(2024, 7, 14, 10, 0),
    )
    booking1 = Booking(time_slot=ts, booker="Jane Doe", attendees=5)
    booking2 = Booking(time_slot=ts, booker="Jane Doe", attendees=5)

    object.__setattr__(booking2, "booking_id", booking1.booking_id)

    assert hash(booking1) == hash(booking2)
    assert len({booking1, booking2}) == 1
