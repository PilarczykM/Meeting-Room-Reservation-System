import logging

from src.application.commands.commands import CreateBookingCommand
from src.application.dtos.booking_response import BookingResponse
from src.domain.aggregates.meeting_room import MeetingRoom
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

        # Get or create the meeting room (assuming single room with ID "main-room")
        room_id = "main-room"
        meeting_room = self.booking_repository.find_by_id(room_id)
        if meeting_room is None:
            meeting_room = MeetingRoom(room_id=room_id)

        # Create the booking
        timeslot = TimeSlot.create(request.start_time.isoformat(), request.end_time.isoformat())

        try:
            # Use the meeting room aggregate to create the booking
            booking = meeting_room.book(timeslot, request.booker, request.attendees)

            # Save the updated meeting room
            self.booking_repository.save(meeting_room)

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
