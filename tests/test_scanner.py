from unittest.mock import MagicMock

import responses as resp

from global_entry_scanner.models import Appointment, Location
from global_entry_scanner.notifications.base import Notifier
from global_entry_scanner.scanner import APPOINTMENTS_API_URL, LOCATIONS_API_URL, Scanner
from tests.conftest import MOCK_APPOINTMENTS, MOCK_LOCATIONS


@resp.activate
def test_fetch_locations_returns_dict_keyed_by_id() -> None:
    resp.add(resp.GET, LOCATIONS_API_URL, json=MOCK_LOCATIONS)
    scanner = Scanner(location_ids=[5001])
    locations = scanner.fetch_locations()
    assert 5001 in locations
    assert isinstance(locations[5001], Location)
    assert locations[5001].city == "Mission"
    assert locations[5001].timezone == "America/Chicago"


@resp.activate
def test_fetch_locations_returns_empty_dict_on_network_error() -> None:
    resp.add(resp.GET, LOCATIONS_API_URL, body=ConnectionError("network down"))
    scanner = Scanner(location_ids=[5001])
    locations = scanner.fetch_locations()
    assert locations == {}


@resp.activate
def test_fetch_appointments_returns_list_of_appointments() -> None:
    url = APPOINTMENTS_API_URL.format(5, 5001, 1)
    resp.add(resp.GET, url, json=MOCK_APPOINTMENTS)
    scanner = Scanner(location_ids=[5001])
    appointments = scanner.fetch_appointments(5001)
    assert len(appointments) == 2
    assert isinstance(appointments[0], Appointment)
    assert appointments[0].location_id == 5001
    assert appointments[0].active is True


@resp.activate
def test_fetch_appointments_returns_empty_on_404() -> None:
    url = APPOINTMENTS_API_URL.format(5, 9999, 1)
    resp.add(resp.GET, url, status=404)
    scanner = Scanner(location_ids=[9999])
    appointments = scanner.fetch_appointments(9999)
    assert appointments == []


@resp.activate
def test_fetch_appointments_retries_on_500() -> None:
    url = APPOINTMENTS_API_URL.format(5, 5001, 1)
    resp.add(resp.GET, url, status=500)
    resp.add(resp.GET, url, status=500)
    resp.add(resp.GET, url, json=MOCK_APPOINTMENTS)
    scanner = Scanner(location_ids=[5001])
    appointments = scanner.fetch_appointments(5001)
    assert len(appointments) == 2
    assert len(resp.calls) == 3


@resp.activate
def test_check_once_returns_new_appointments() -> None:
    resp.add(resp.GET, LOCATIONS_API_URL, json=MOCK_LOCATIONS)
    url = APPOINTMENTS_API_URL.format(5, 5001, 1)
    resp.add(resp.GET, url, json=MOCK_APPOINTMENTS)
    scanner = Scanner(location_ids=[5001])
    results = scanner.check_once()
    assert len(results) == 1
    assert results[0].location_id == 5001
    assert results[0].city == "Mission"
    assert len(results[0].new_appointments) == 2
    assert results[0].error is None


@resp.activate
def test_check_once_deduplicates_appointments() -> None:
    resp.add(resp.GET, LOCATIONS_API_URL, json=MOCK_LOCATIONS)
    url = APPOINTMENTS_API_URL.format(5, 5001, 1)
    resp.add(resp.GET, url, json=MOCK_APPOINTMENTS)
    resp.add(resp.GET, url, json=MOCK_APPOINTMENTS)
    scanner = Scanner(location_ids=[5001])
    first = scanner.check_once()
    second = scanner.check_once()
    assert len(first[0].new_appointments) == 2
    assert len(second[0].new_appointments) == 0


@resp.activate
def test_check_once_records_error_in_result() -> None:
    resp.add(resp.GET, LOCATIONS_API_URL, json=MOCK_LOCATIONS)
    url = APPOINTMENTS_API_URL.format(5, 5001, 1)
    resp.add(resp.GET, url, body=ConnectionError("down"))
    scanner = Scanner(location_ids=[5001])
    results = scanner.check_once()
    assert results[0].error is not None


def test_notify_all_calls_every_notifier() -> None:
    n1: MagicMock = MagicMock(spec=Notifier)
    n2: MagicMock = MagicMock(spec=Notifier)
    scanner = Scanner(location_ids=[5001])
    scanner.add_notifier(n1)
    scanner.add_notifier(n2)
    scanner._notify_all("subject", "message")
    n1.send.assert_called_once_with("subject", "message")
    n2.send.assert_called_once_with("subject", "message")


def test_notify_all_continues_when_one_notifier_fails() -> None:
    n1: MagicMock = MagicMock(spec=Notifier)
    n1.send.side_effect = RuntimeError("slack down")
    n2: MagicMock = MagicMock(spec=Notifier)
    scanner = Scanner(location_ids=[5001])
    scanner.add_notifier(n1)
    scanner.add_notifier(n2)
    scanner._notify_all("subject", "message")
    n2.send.assert_called_once_with("subject", "message")


@resp.activate
def test_start_batches_all_slots_into_one_notification() -> None:
    resp.add(resp.GET, LOCATIONS_API_URL, json=MOCK_LOCATIONS)
    url = APPOINTMENTS_API_URL.format(5, 5001, 1)
    # Two slots available on first check, none on second (to stop the loop via KeyboardInterrupt)
    resp.add(resp.GET, url, json=MOCK_APPOINTMENTS)

    notifier: MagicMock = MagicMock(spec=Notifier)
    scanner = Scanner(location_ids=[5001], check_interval=0, error_interval=0)
    scanner.add_notifier(notifier)

    # Patch time.sleep to raise KeyboardInterrupt after first iteration
    call_count = 0

    def stop_after_first(seconds: float) -> None:
        nonlocal call_count
        call_count += 1
        raise KeyboardInterrupt

    import unittest.mock as mock
    with mock.patch("global_entry_scanner.scanner.time.sleep", side_effect=stop_after_first):
        scanner.start()

    # 2 slots → exactly 1 notification (not 2)
    assert notifier.send.call_count == 1
    subject, message = notifier.send.call_args[0]
    assert "2 new slots" in subject
    assert "Mission" in message
    assert "10:25" in message
    assert "11:25" in message
