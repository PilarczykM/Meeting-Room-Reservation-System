import logging

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.entities.booking import Booking
from src.domain.entities.timeslot import TimeSlot

logger = logging.getLogger(__name__)


class BookingService:
    """Service for managing booking operations."""

    def __init__(self, booking_repository):
        self.booking_repository = booking_repository

    def create_booking(self, start_time, end_time, booker_id, attendees):
        """Create a new booking for a meeting room."""
        logger.info(
            f"Attempting to create booking for {booker_id} from {start_time} to {end_time} with {attendees} attendees."
        )
        existing_bookings = self.booking_repository.get_all()
        meeting_room = MeetingRoom(bookings=existing_bookings)
        timeslot = TimeSlot.create(start_time, end_time)
        booking = Booking.create(timeslot, booker_id, attendees)
        try:
            meeting_room.book(booking.time_slot, booking.booker, booking.attendees)
            self.booking_repository.add(booking)
            logger.info(f"Booking created successfully: {booking.booking_id}")
        except Exception:
            logger.exception("Failed to create booking")
            raise  # Re-raise the exception after logging
