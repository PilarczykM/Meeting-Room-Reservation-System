from datetime import datetime

from pydantic import BaseModel, Field


class BookingResponse(BaseModel):
    """Represents the response data for a booking."""

    booking_id: str = Field(..., description="The unique ID of the booking.")
    start_time: datetime = Field(..., description="The start time of the booking.")
    end_time: datetime = Field(..., description="The end time of the booking.")
    booker: str = Field(..., description="The name or ID of the person who booked.")
    attendees: int = Field(..., description="The number of attendees for the meeting.")
