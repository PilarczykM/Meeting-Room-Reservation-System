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
def time_slot_1(parse_time):
    return TimeSlot(
        start_time=parse_time("09:00"),
        end_time=parse_time("10:00"),
    )


@pytest.fixture
def time_slot_2(parse_time):
    return TimeSlot(
        start_time=parse_time("10:00"),
        end_time=parse_time("11:00"),
    )


@pytest.fixture
def overlapping_time_slot(parse_time):
    return TimeSlot(
        start_time=parse_time("09:30"),
        end_time=parse_time("10:30"),
    )
