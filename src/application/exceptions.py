class ApplicationError(Exception):
    """Base exception for application-level errors."""

    pass


class CancellationFailedError(ApplicationError):
    """Exception raised when a booking cancellation fails."""

    pass
