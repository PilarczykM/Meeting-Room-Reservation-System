from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class BookingRequest(BaseModel):
    """Represents a request to create a new booking."""

    start_time: datetime = Field(..., description="The start time of the booking.")
    end_time: datetime = Field(..., description="The end time of the booking.")
    booker: str = Field(..., min_length=1, description="The name or ID of the person booking.")
    attendees: int = Field(..., ge=4, le=20, description="The number of attendees for the meeting.")

    @model_validator(mode="after")
    def validate_times(self):
        """Validate that the end time is after the start time."""
        if self.start_time >= self.end_time:
            raise ValueError("End time must be after start time.")
        return self
