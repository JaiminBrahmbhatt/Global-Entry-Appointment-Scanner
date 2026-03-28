MOCK_LOCATIONS = [
    {
        "id": 5001,
        "name": "Hidalgo Enrollment Center",
        "shortName": "Hidalgo Enrollment Center",
        "locationType": "LND",
        "city": "Mission",
        "state": "TX",
        "tzData": "America/Chicago",
    },
    {
        "id": 5140,
        "name": "Chicago O'Hare International Airport",
        "shortName": "Chicago O'Hare",
        "locationType": "AP",
        "city": "Chicago",
        "state": "IL",
        "tzData": "America/Chicago",
    },
]

MOCK_APPOINTMENTS = [
    {
        "locationId": 5001,
        "startTimestamp": "2026-04-13T10:25",
        "endTimestamp": "2026-04-13T10:35",
        "active": True,
        "duration": 10,
        "remoteInd": False,
    },
    {
        "locationId": 5001,
        "startTimestamp": "2026-04-13T11:25",
        "endTimestamp": "2026-04-13T11:35",
        "active": True,
        "duration": 10,
        "remoteInd": False,
    },
]

import pytest
from global_entry_scanner.scanner import _locations_cache


@pytest.fixture(autouse=True)
def clear_locations_cache() -> None:  # type: ignore[return]
    _locations_cache.clear()
    yield  # type: ignore[misc]
    _locations_cache.clear()
