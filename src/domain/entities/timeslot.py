from datetime import datetime, timezone
from typing import Self

from pydantic import BaseModel, Field, model_validator


class TimeSlot(BaseModel):
    """Represents a time slot with a start and end time."""

    start_time: datetime = Field(..., description="The start time of the time slot.")
    end_time: datetime = Field(..., description="The end time of the time slot.")

    @model_validator(mode="after")
    def validate_times(self) -> Self:
        """Validate that the end time is after the start time."""
        if self.start_time >= self.end_time:
            raise ValueError("End time must be after start time.")
        return self

    def overlaps_with(self, other: Self) -> bool:
        """Check if this time slot overlaps with another time slot."""
        return not (
            self.end_time <= other.start_time or self.start_time >= other.end_time
        )

    def __eq__(self, other: object) -> bool:
        """Compare two TimeSlot objects for equality."""
        if not isinstance(other, TimeSlot):
            return NotImplemented
        return self.start_time == other.start_time and self.end_time == other.end_time

    def __lt__(self, other: Self) -> bool:
        """Compare if this time slot ends before another time slot starts."""
        return self.end_time <= other.start_time

    def __gt__(self, other: Self) -> bool:
        """Compare if this time slot starts after another time slot ends."""
        return self.start_time >= other.end_time

    def __le__(self, other: Self) -> bool:
        """Compare if this time slot ends at or before another time slot starts."""
        return self.end_time <= other.start_time

    def __ge__(self, other: Self) -> bool:
        """Compare if this time slot starts at or after another time slot ends."""
        return self.start_time >= other.end_time

    def __hash__(self) -> int:
        """Return the hash of the TimeSlot object."""
        return hash((self.start_time, self.end_time))

    def to_utc(self) -> Self:
        """Convert the time slot to UTC if timezone information is missing."""
        if self.start_time.tzinfo is None:
            self.start_time = self.start_time.replace(tzinfo=timezone.utc)
        if self.end_time.tzinfo is None:
            self.end_time = self.end_time.replace(tzinfo=timezone.utc)
        return self
