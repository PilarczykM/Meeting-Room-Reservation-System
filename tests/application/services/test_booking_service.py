import logging
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from src.application.dtos.booking_request import BookingRequest
from src.application.dtos.commands import CreateBookingCommand
from src.application.services.booking_service import BookingService
from src.domain.entities.booking import Booking
from src.domain.entities.timeslot import TimeSlot
from src.domain.exceptions import OverlappingBookingError


@pytest.fixture
def booking_service():
    booking_repository = MagicMock()
    return BookingService(booking_repository)


def test_create_booking_success(booking_service):
    # Arrange
    request = BookingRequest(
        start_time=datetime(2025, 7, 15, 10, 0, 0),
        end_time=datetime(2025, 7, 15, 11, 0, 0),
        booker="user123",
        attendees=10,
    )
    command = CreateBookingCommand(request=request)

    # Act
    response = booking_service.create_booking(command)

    # Assert
    booking_service.booking_repository.add.assert_called_once()
    assert response.booker == request.booker
    assert response.attendees == request.attendees


def test_create_booking_overlapping_error(booking_service):
    # Arrange
    request = BookingRequest(
        start_time=datetime(2025, 7, 15, 10, 0, 0),
        end_time=datetime(2025, 7, 15, 11, 0, 0),
        booker="user123",
        attendees=10,
    )
    command = CreateBookingCommand(request=request)

    existing_timeslot = TimeSlot.create(request.start_time.isoformat(), request.end_time.isoformat())
    existing_booking = Booking.create(existing_timeslot, request.booker, request.attendees)

    # Mock the repository to return an existing booking
    booking_service.booking_repository.get_all.return_value = [existing_booking]

    # Act & Assert
    with pytest.raises(OverlappingBookingError):
        booking_service.create_booking(command)


def test_booking_request_invalid_attendees_validation():
    # Arrange
    # Act & Assert
    with pytest.raises(ValidationError):
        BookingRequest(
            start_time=datetime(2025, 7, 15, 10, 0, 0),
            end_time=datetime(2025, 7, 15, 11, 0, 0),
            booker="user123",
            attendees=2,  # Invalid number of attendees
        )


def test_create_booking_logging(booking_service, caplog):
    # Arrange
    request = BookingRequest(
        start_time=datetime(2025, 7, 15, 10, 0, 0),
        end_time=datetime(2025, 7, 15, 11, 0, 0),
        booker="user123",
        attendees=10,
    )
    command = CreateBookingCommand(request=request)

    with caplog.at_level(logging.INFO):
        booking_service.create_booking(command)
        assert f"Attempting to create booking for {request.booker}" in caplog.messages[0]
        assert "Booking created successfully" in caplog.messages[1]
