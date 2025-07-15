from datetime import datetime

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
        raise OverlappingBookingError(datetime.utcnow(), datetime.utcnow())


def test_invalid_attendee_count_error():
    with pytest.raises(InvalidAttendeeCountError):
        raise InvalidAttendeeCountError(3)


def test_booking_not_found_error():
    with pytest.raises(BookingNotFoundError, match="Booking not found."):
        raise BookingNotFoundError("123")


def test_invalid_time_slot_error():
    with pytest.raises(InvalidTimeSlotError):
        raise InvalidTimeSlotError(datetime.utcnow(), datetime.utcnow())


def test_exception_inheritance():
    # All custom exceptions should inherit from DomainError
    assert issubclass(OverlappingBookingError, DomainError)
    assert issubclass(InvalidAttendeeCountError, DomainError)
    assert issubclass(BookingNotFoundError, DomainError)
    assert issubclass(InvalidTimeSlotError, DomainError)
