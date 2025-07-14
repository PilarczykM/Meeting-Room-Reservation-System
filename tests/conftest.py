from datetime import datetime

import pytest

from src.domain.entities.timeslot import TimeSlot


@pytest.fixture
def base_date():
    return datetime(2024, 7, 14)


@pytest.fixture
def parse_time(base_date):
    def _parse_time(t_str):
        h, m = map(int, t_str.split(":"))
        return base_date.replace(hour=h, minute=m, second=0, microsecond=0)

    return _parse_time


@pytest.fixture
def sample_timeslot():
    start = datetime(2024, 7, 14, 9, 0, 0)
    end = datetime(2024, 7, 14, 10, 0, 0)
    return TimeSlot(start_time=start, end_time=end)


@pytest.fixture
def time_slot_1():
    return TimeSlot(
        start_time=datetime(2024, 7, 14, 9, 0),
        end_time=datetime(2024, 7, 14, 10, 0),
    )


@pytest.fixture
def time_slot_2():
    return TimeSlot(
        start_time=datetime(2024, 7, 14, 10, 0),
        end_time=datetime(2024, 7, 14, 11, 0),
    )


@pytest.fixture
def overlapping_time_slot():
    return TimeSlot(
        start_time=datetime(2024, 7, 14, 9, 30),
        end_time=datetime(2024, 7, 14, 10, 30),
    )
