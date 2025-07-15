import logging

from src.application.commands.commands import CreateBookingCommand
from src.application.dtos.booking_response import BookingResponse
from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.entities.booking import Booking
from src.domain.entities.timeslot import TimeSlot
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository

logger = logging.getLogger(__name__)


class BookingService:
    """Service for managing booking operations."""

    def __init__(self, booking_repository: MeetingRoomRepository):
        self.booking_repository = booking_repository

    def create_booking(self, command: CreateBookingCommand) -> BookingResponse:
        """Create a new booking for a meeting room."""
        request = command.request
        logger.info(
            f"Attempting to create booking for {request.booker} from "
            f"{request.start_time} to {request.end_time} with {request.attendees} attendees."
        )
        existing_bookings = self.booking_repository.get_all()
        meeting_room = MeetingRoom(bookings=existing_bookings)
        timeslot = TimeSlot.create(request.start_time.isoformat(), request.end_time.isoformat())
        booking = Booking.create(timeslot, request.booker, request.attendees)
        try:
            meeting_room.book(booking.time_slot, booking.booker, booking.attendees)
            self.booking_repository.add(booking)
            logger.info(f"Booking created successfully: {booking.booking_id}")
            return BookingResponse(
                booking_id=booking.booking_id,
                start_time=booking.time_slot.start_time,
                end_time=booking.time_slot.end_time,
                booker=booking.booker,
                attendees=booking.attendees,
            )
        except Exception:
            logger.exception("Failed to create booking")
            raise  # Re-raise the exception after logging
