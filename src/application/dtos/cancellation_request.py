from pydantic import BaseModel, Field


class CancellationRequest(BaseModel):
    """Represents a request to cancel an existing booking."""

    booking_id: str = Field(..., description="The ID of the booking to cancel.")
