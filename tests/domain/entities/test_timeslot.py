from datetime import timezone

import pytest

from src.domain.entities.timeslot import TimeSlot
from src.domain.exceptions import InvalidTimeSlotError


def test_timeslot_creation_valid(parse_time):
    start = parse_time("09:00")
    end = parse_time("10:00")
    timeslot = TimeSlot(start_time=start, end_time=end)
    assert timeslot.start_time == start
    assert timeslot.end_time == end


def test_timeslot_creation_invalid_end_before_start(parse_time):
    start = parse_time("10:00")
    end = parse_time("09:00")
    with pytest.raises(InvalidTimeSlotError):
        TimeSlot(start_time=start, end_time=end)


def test_timeslot_creation_invalid_end_equals_start(parse_time):
    start = parse_time("09:00")
    end = parse_time("09:00")
    with pytest.raises(InvalidTimeSlotError):
        TimeSlot(start_time=start, end_time=end)


@pytest.mark.parametrize(
    "ts1_start, ts1_end, ts2_start, ts2_end, expected_overlap",
    [
        # No overlap
        ("09:00", "10:00", "10:00", "11:00", False),  # Adjacent, no overlap
        ("09:00", "10:00", "10:01", "11:00", False),  # Separated
        ("10:00", "11:00", "09:00", "10:00", False),  # Adjacent, no overlap (reversed)
        # Overlap
        (
            "09:00",
            "10:00",
            "09:30",
            "10:30",
            True,
        ),  # Partial overlap (ts2 starts within ts1)
        (
            "09:00",
            "10:00",
            "08:30",
            "09:30",
            True,
        ),  # Partial overlap (ts2 ends within ts1)
        ("09:00", "10:00", "09:00", "10:00", True),  # Exact overlap
        ("09:00", "11:00", "09:30", "10:30", True),  # ts2 fully within ts1
        ("09:30", "10:30", "09:00", "11:00", True),  # ts1 fully within ts2
        ("09:00", "10:00", "08:00", "11:00", True),  # ts1 fully within ts2 (larger)
    ],
)
def test_timeslot_overlaps_with(ts1_start, ts1_end, ts2_start, ts2_end, expected_overlap, parse_time):
    ts1 = TimeSlot(start_time=parse_time(ts1_start), end_time=parse_time(ts1_end))
    ts2 = TimeSlot(start_time=parse_time(ts2_start), end_time=parse_time(ts2_end))

    assert ts1.overlaps_with(ts2) == expected_overlap


def test_timeslot_equality(parse_time):
    ts1 = TimeSlot(
        start_time=parse_time("09:00"),
        end_time=parse_time("10:00"),
    )
    ts2 = TimeSlot(
        start_time=parse_time("09:00"),
        end_time=parse_time("10:00"),
    )
    ts3 = TimeSlot(
        start_time=parse_time("09:00"),
        end_time=parse_time("10:30"),
    )

    assert ts1 == ts2
    assert ts1 != ts3


def test_timeslot_comparison_operators(parse_time):
    ts1 = TimeSlot(
        start_time=parse_time("09:00"),
        end_time=parse_time("10:00"),
    )
    ts2 = TimeSlot(
        start_time=parse_time("10:00"),
        end_time=parse_time("11:00"),
    )
    ts3 = TimeSlot(
        start_time=parse_time("08:00"),
        end_time=parse_time("09:00"),
    )

    assert ts1 < ts2  # ts1 ends when ts2 starts
    assert ts1 <= ts2
    assert ts2 > ts1
    assert ts2 >= ts1
    assert ts1 > ts3  # ts1 starts when ts3 ends
    assert ts1 >= ts3
    assert ts3 < ts1
    assert ts3 <= ts1


def test_timeslot_hashable(parse_time):
    ts1 = TimeSlot(
        start_time=parse_time("09:00"),
        end_time=parse_time("10:00"),
    )
    ts2 = TimeSlot(
        start_time=parse_time("09:00"),
        end_time=parse_time("10:00"),
    )
    assert hash(ts1) == hash(ts2)
    assert len({ts1, ts2}) == 1


def test_timeslot_to_utc_no_tzinfo(parse_time):
    start = parse_time("09:00")
    end = parse_time("10:00")
    timeslot = TimeSlot(start_time=start, end_time=end)
    utc_timeslot = timeslot.to_utc()

    assert utc_timeslot.start_time.tzinfo == timezone.utc
    assert utc_timeslot.end_time.tzinfo == timezone.utc
    assert utc_timeslot.start_time.hour == 9
    assert utc_timeslot.end_time.hour == 10


def test_timeslot_to_utc_with_tzinfo(parse_time):
    start = parse_time("09:00").replace(tzinfo=timezone.utc)
    end = parse_time("10:00").replace(tzinfo=timezone.utc)
    timeslot = TimeSlot(start_time=start, end_time=end)
    utc_timeslot = timeslot.to_utc()

    assert utc_timeslot.start_time.tzinfo == timezone.utc
    assert utc_timeslot.end_time.tzinfo == timezone.utc
    assert utc_timeslot.start_time.hour == 9
    assert utc_timeslot.end_time.hour == 10
