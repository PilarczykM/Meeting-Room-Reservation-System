class DomainError(Exception):
    """Base class for domain-specific exceptions."""

    pass


class OverlappingBookingError(DomainError):
    """Exception raised when a booking overlaps with an existing one."""

    def __init__(self, message="The requested time slot overlaps with an existing booking."):
        self.message = message
        super().__init__(self.message)


class InvalidAttendeeCountError(DomainError):
    """Exception raised when the number of attendees is outside the allowed range."""

    def __init__(self, message="Number of attendees must be between 4 and 20 (inclusive)."):
        self.message = message
        super().__init__(self.message)


class BookingNotFoundError(DomainError):
    """Exception raised when a booking is not found."""

    def __init__(self, message="Booking not found."):
        self.message = message
        super().__init__(self.message)


class InvalidTimeSlotError(DomainError):
    """Exception raised when a time slot is invalid (e.g., end time before start time)."""

    def __init__(self, message="End time must be after start time."):
        self.message = message
        super().__init__(self.message)
