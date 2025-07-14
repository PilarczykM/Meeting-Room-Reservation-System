from datetime import datetime

import pytest


@pytest.fixture
def base_date():
    return datetime(2024, 7, 14)


@pytest.fixture
def parse_time(base_date):
    def _parse_time(t_str):
        h, m = map(int, t_str.split(":"))
        return base_date.replace(hour=h, minute=m, second=0, microsecond=0)

    return _parse_time
