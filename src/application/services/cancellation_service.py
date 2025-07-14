import logging

from src.application.exceptions import CancellationFailedError

logger = logging.getLogger(__name__)


class CancellationService:
    """Service for managing booking cancellations."""

    def __init__(self, booking_repository):
        self.booking_repository = booking_repository

    def cancel_booking(self, booking_id: str):
        """Cancel an existing booking by its ID."""
        logger.info(f"Attempting to cancel booking with ID: {booking_id}")
        booking = self.booking_repository.get_by_id(booking_id)
        if not booking:
            logger.warning(f"Booking with ID {booking_id} not found for cancellation.")
            raise CancellationFailedError(f"Cancellation failed: Booking with ID {booking_id} not found.")
        try:
            self.booking_repository.delete(booking_id)
            logger.info(f"Booking with ID {booking_id} cancelled successfully.")
        except Exception as e:
            logger.exception("Failed to cancel booking")
            raise CancellationFailedError(f"Cancellation failed: {e}") from e
