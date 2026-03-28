from datetime import datetime, timezone

from global_entry_scanner.models import Appointment, Location, ScanResult


def test_location_stores_fields() -> None:
    loc = Location(
        id=5001, name="Chicago O'Hare", city="Chicago", state="IL", timezone="America/Chicago"
    )
    assert loc.id == 5001
    assert loc.city == "Chicago"
    assert loc.timezone == "America/Chicago"


def test_appointment_stores_fields() -> None:
    start = datetime(2026, 4, 13, 10, 25, tzinfo=timezone.utc)
    end = datetime(2026, 4, 13, 10, 35, tzinfo=timezone.utc)
    appt = Appointment(location_id=5001, start=start, end=end, active=True)
    assert appt.location_id == 5001
    assert appt.active is True


def test_scan_result_with_no_error() -> None:
    result = ScanResult(location_id=5001, city="Chicago", new_appointments=[], error=None)
    assert result.error is None
    assert result.new_appointments == []


def test_scan_result_with_error() -> None:
    result = ScanResult(location_id=5001, city="Chicago", new_appointments=[], error="timeout")
    assert result.error == "timeout"
