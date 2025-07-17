import logging

from src.application.commands.commands import CancelBookingCommand
from src.application.exceptions import CancellationFailedError
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository

logger = logging.getLogger(__name__)


class CancellationService:
    """Service for managing booking cancellations."""

    def __init__(self, booking_repository: MeetingRoomRepository):
        self.booking_repository = booking_repository

    def cancel_booking(self, command: CancelBookingCommand):
        """Cancel an existing booking by its ID."""
        booking_id = command.request.booking_id
        logger.info(f"Attempting to cancel booking with ID: {booking_id}")

        # Find the meeting room that contains the booking
        room_id = "main-room"  # Assuming single room
        meeting_room = self.booking_repository.find_by_id(room_id)

        if not meeting_room:
            logger.warning(f"Meeting room {room_id} not found.")
            raise CancellationFailedError("Cancellation failed: Meeting room not found.")

        # Find the booking in the meeting room
        booking_to_cancel = None
        for booking in meeting_room.bookings:
            if booking.booking_id == booking_id:
                booking_to_cancel = booking
                break

        if not booking_to_cancel:
            logger.warning(f"Booking with ID {booking_id} not found for cancellation.")
            raise CancellationFailedError(f"Cancellation failed: Booking with ID {booking_id} not found.")

        try:
            # Use the meeting room aggregate to cancel the booking
            meeting_room.cancel_booking(booking_id)

            # Save the updated meeting room
            self.booking_repository.save(meeting_room)

            logger.info(f"Booking with ID {booking_id} cancelled successfully.")
        except Exception as e:
            logger.exception("Failed to cancel booking")
            raise CancellationFailedError(f"Cancellation failed: {e}") from e
