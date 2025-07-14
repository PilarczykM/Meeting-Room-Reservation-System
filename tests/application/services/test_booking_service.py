import unittest
from unittest.mock import MagicMock

from src.application.services.booking_service import BookingService


class TestBookingService(unittest.TestCase):
    def setUp(self):
        self.booking_repository = MagicMock()
        self.booking_service = BookingService(self.booking_repository)

    def test_create_booking_success(self):
        # Arrange
        start_time = "2025-07-15T10:00:00"
        end_time = "2025-07-15T11:00:00"
        booker_id = "user123"
        attendees = 10

        # Act
        self.booking_service.create_booking(start_time, end_time, booker_id, attendees)

        # Assert
        self.booking_repository.add.assert_called_once()

    def test_create_booking_overlapping_error(self):
        # Arrange
        start_time = "2025-07-15T10:00:00"
        end_time = "2025-07-15T11:00:00"
        booker_id = "user123"
        attendees = 10

        from src.domain.entities.booking import Booking
        from src.domain.entities.timeslot import TimeSlot
        from src.domain.exceptions import OverlappingBookingError

        existing_timeslot = TimeSlot.create(start_time, end_time)
        existing_booking = Booking.create(existing_timeslot, booker_id, attendees)

        # Mock the repository to return an existing booking
        self.booking_repository.get_all.return_value = [existing_booking]

        # Act & Assert
        with self.assertRaises(OverlappingBookingError):
            self.booking_service.create_booking(start_time, end_time, booker_id, attendees)

    def test_create_booking_invalid_attendees_error(self):
        # Arrange
        start_time = "2025-07-15T10:00:00"
        end_time = "2025-07-15T11:00:00"
        booker_id = "user123"
        attendees = 2  # Invalid number of attendees

        from src.domain.exceptions import InvalidAttendeeCountError

        # Act & Assert
        with self.assertRaises(InvalidAttendeeCountError):
            self.booking_service.create_booking(start_time, end_time, booker_id, attendees)

    def test_create_booking_logging(self):
        # Arrange
        start_time = "2025-07-15T10:00:00"
        end_time = "2025-07-15T11:00:00"
        booker_id = "user123"
        attendees = 10

        with self.assertLogs("src.application.services.booking_service", level="INFO") as cm:
            self.booking_service.create_booking(start_time, end_time, booker_id, attendees)
            self.assertIn(f"Attempting to create booking for {booker_id}", cm.output[0])
            self.assertIn("Booking created successfully", cm.output[1])


if __name__ == "__main__":
    unittest.main()
