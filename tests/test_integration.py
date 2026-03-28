"""Integration tests — hit the live CBP API. Run with: pytest -m integration"""
import pytest

from global_entry_scanner.scanner import Scanner


@pytest.mark.integration
def test_fetch_locations_live() -> None:
    scanner = Scanner(location_ids=[])
    locs = scanner.fetch_locations()
    assert len(locs) > 50
    assert 5001 in locs
    assert locs[5001].city == "Mission"


@pytest.mark.integration
def test_fetch_appointments_live() -> None:
    scanner = Scanner(location_ids=[5001])
    appointments = scanner.fetch_appointments(5001)
    assert isinstance(appointments, list)
