import uuid
from typing import Self

from pydantic import BaseModel, Field, model_validator

from src.domain.entities.timeslot import TimeSlot
from src.domain.exceptions import InvalidAttendeeCountError


class Booking(BaseModel):
    """Represents a booking for a meeting room."""

    booking_id: str = Field(default_factory=lambda: str(uuid.uuid4()), frozen=True)
    time_slot: TimeSlot = Field(..., description="The time slot for the booking.")
    booker: str = Field(..., description="The name or ID of the person booking.")
    attendees: int = Field(..., description="The number of attendees for the meeting.")

    @classmethod
    def create(cls, time_slot: TimeSlot, booker: str, attendees: int, booking_id: str | None = None) -> Self:
        """Create a Booking instance."""
        if booking_id is None:
            return cls(time_slot=time_slot, booker=booker, attendees=attendees)
        else:
            return cls(booking_id=booking_id, time_slot=time_slot, booker=booker, attendees=attendees)

    @model_validator(mode="after")
    def validate_attendees(self) -> Self:
        """Validate that the number of attendees is within the allowed range."""
        if not (4 <= self.attendees <= 20):
            raise InvalidAttendeeCountError()
        return self

    def __eq__(self, other: object) -> bool:
        """Compare two Booking objects for equality based on their booking_id."""
        if not isinstance(other, Booking):
            return NotImplemented
        return self.booking_id == other.booking_id

    def __hash__(self) -> int:
        """Return the hash of the Booking object based on its booking_id."""
        return hash(self.booking_id)
