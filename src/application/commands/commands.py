from pydantic import BaseModel

from src.application.dtos.booking_request import BookingRequest
from src.application.dtos.cancellation_request import CancellationRequest


class CreateBookingCommand(BaseModel):
    """Command to create a new booking."""

    request: BookingRequest


class CancelBookingCommand(BaseModel):
    """Command to cancel an existing booking."""

    request: CancellationRequest
