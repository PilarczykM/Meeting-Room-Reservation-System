import logging

logger = logging.getLogger(__name__)


class QueryService:
    """Service for handling read operations on bookings."""

    def __init__(self, booking_repository):
        self.booking_repository = booking_repository

    def get_all_bookings(self) -> list[dict]:
        """Retrieve all bookings and format them for display."""
        logger.info("Retrieving all bookings.")
        bookings = self.booking_repository.get_all()
        formatted_bookings = []
        for booking in bookings:
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
