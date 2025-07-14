from datetime import datetime, timedelta

import pytest

from src.application.commands.commands import CancelBookingCommand, CreateBookingCommand
from src.application.dtos.booking_request import BookingRequest
from src.application.dtos.booking_response import BookingResponse
from src.application.dtos.cancellation_request import CancellationRequest


def test_booking_request_valid_data():
    request = BookingRequest(
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        booker="test_booker",
        attendees=10,
    )
    assert isinstance(request, BookingRequest)


def test_booking_request_invalid_attendees():
    with pytest.raises(ValueError):
        BookingRequest(
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            booker="test_booker",
            attendees=2,
        )


def test_booking_request_invalid_time_range():
    with pytest.raises(ValueError):
        BookingRequest(
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now(),
            booker="test_booker",
            attendees=10,
        )


def test_cancellation_request_valid_data():
    request = CancellationRequest(booking_id="test_id")
    assert isinstance(request, CancellationRequest)


def test_booking_response_valid_data():
    response = BookingResponse(
        booking_id="test_id",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        booker="test_booker",
        attendees=10,
    )
    assert isinstance(response, BookingResponse)


def test_create_booking_command_valid_data():
    request = BookingRequest(
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        booker="test_booker",
        attendees=10,
    )
    command = CreateBookingCommand(request=request)
    assert isinstance(command, CreateBookingCommand)


def test_cancel_booking_command_valid_data():
    request = CancellationRequest(booking_id="test_id")
    command = CancelBookingCommand(request=request)
    assert isinstance(command, CancelBookingCommand)
