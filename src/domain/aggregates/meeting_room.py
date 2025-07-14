import uuid

from pydantic import BaseModel, Field

from src.domain.entities.booking import Booking
from src.domain.entities.timeslot import TimeSlot
from src.domain.exceptions import (
    BookingNotFoundError,
    InvalidAttendeeCountError,
    OverlappingBookingError,
)


class MeetingRoom(BaseModel):
    """Represents a meeting room aggregate root."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capacity: int = Field(default=20)
    bookings: list[Booking] = Field(default_factory=list)

    def book(self, time_slot: TimeSlot, booker: str, attendees: int) -> Booking:
        """Books the meeting room for a given time slot."""
        if not (4 <= attendees <= self.capacity):
            raise InvalidAttendeeCountError(f"Number of attendees must be between 4 and {self.capacity} (inclusive).")

        for existing_booking in self.bookings:
            if time_slot.overlaps_with(existing_booking.time_slot):
                raise OverlappingBookingError(
                    f"The time slot {time_slot.start_time}-{time_slot.end_time} overlaps with an existing booking."
                )

        new_booking = Booking(time_slot=time_slot, booker=booker, attendees=attendees)
        self.bookings.append(new_booking)
        return new_booking

    def cancel(self, booking_id: str) -> None:
        """Cancel a booking by its ID."""
        initial_len = len(self.bookings)
        self.bookings = [b for b in self.bookings if b.booking_id != booking_id]
        if len(self.bookings) == initial_len:
            raise BookingNotFoundError(f"Booking with ID {booking_id} not found.")

    def list_bookings(self) -> list[Booking]:
        """List all current bookings for the meeting room."""
        return sorted(self.bookings, key=lambda b: b.time_slot.start_time)
