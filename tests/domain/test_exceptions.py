import pytest

from src.domain.exceptions import (
    BookingNotFoundError,
    DomainError,
    InvalidAttendeeCountError,
    InvalidTimeSlotError,
    OverlappingBookingError,
)


def test_domain_error_base_class():
    with pytest.raises(DomainError, match="Base domain error"):
        raise DomainError("Base domain error")


def test_overlapping_booking_error():
    with pytest.raises(OverlappingBookingError, match="The requested time slot overlaps with an existing booking."):
        raise OverlappingBookingError()

    with pytest.raises(OverlappingBookingError, match="Custom overlap message"):
        raise OverlappingBookingError("Custom overlap message")


def test_invalid_attendee_count_error():
    with pytest.raises(
        InvalidAttendeeCountError, match="Number of attendees must be between 4 and 20 \\(inclusive\\)\\."
    ):
        raise InvalidAttendeeCountError()

    with pytest.raises(InvalidAttendeeCountError, match="Custom attendee message"):
        raise InvalidAttendeeCountError("Custom attendee message")


def test_booking_not_found_error():
    with pytest.raises(BookingNotFoundError, match="Booking not found."):
        raise BookingNotFoundError()

    with pytest.raises(BookingNotFoundError, match="Custom not found message"):
        raise BookingNotFoundError("Custom not found message")


def test_invalid_time_slot_error():
    with pytest.raises(InvalidTimeSlotError, match="End time must be after start time."):
        raise InvalidTimeSlotError()

    with pytest.raises(InvalidTimeSlotError, match="Custom time slot message"):
        raise InvalidTimeSlotError("Custom time slot message")


def test_exception_inheritance():
    # All custom exceptions should inherit from DomainError
    assert issubclass(OverlappingBookingError, DomainError)
    assert issubclass(InvalidAttendeeCountError, DomainError)
    assert issubclass(BookingNotFoundError, DomainError)
    assert issubclass(InvalidTimeSlotError, DomainError)
