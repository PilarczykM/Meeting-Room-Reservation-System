import logging

from src.domain.repositories.meeting_room_repository import MeetingRoomRepository

logger = logging.getLogger(__name__)


class QueryService:
    """Service for handling read operations on bookings."""

    def __init__(self, booking_repository: MeetingRoomRepository):
        self.booking_repository = booking_repository

    def get_all_bookings(self) -> list[dict]:
        """Retrieve all bookings and format them for display."""
        logger.info("Retrieving all bookings.")

        # Get all meeting rooms and extract bookings from them
        meeting_rooms = self.booking_repository.find_all()
        formatted_bookings = []

        for room in meeting_rooms:
            for booking in room.bookings:
                formatted_bookings.append(
                    {
                        "booking_id": booking.booking_id,
                        "start_time": booking.time_slot.start_time.isoformat(),
                        "end_time": booking.time_slot.end_time.isoformat(),
                        "booker": booking.booker,
                        "attendees": booking.attendees,
                    }
                )

        logger.info(f"Retrieved {len(formatted_bookings)} bookings.")
        return formatted_bookings
