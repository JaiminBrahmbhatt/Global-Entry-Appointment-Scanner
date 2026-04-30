from __future__ import annotations

from datetime import datetime
from io import StringIO
from unittest import mock

from rich.console import Console

from global_entry_scanner.models import Location, ScanResult


def _test_console() -> Console:
    return Console(file=StringIO(), no_color=True, width=200)


def test_print_locations_table_contains_location_data() -> None:
    from global_entry_scanner.display import print_locations_table

    locs = {
        5001: Location(
            id=5001,
            name="Hidalgo Enrollment Center",
            city="Mission",
            state="TX",
            timezone="America/Chicago",
        ),
        5140: Location(
            id=5140,
            name="Chicago O'Hare International Airport",
            city="Chicago",
            state="IL",
            timezone="America/Chicago",
        ),
    }
    test_con = _test_console()
    with mock.patch("global_entry_scanner.display.console", test_con):
        print_locations_table(locs)

    output = test_con.file.getvalue()  # type: ignore[union-attr]
    assert "5001" in output
    assert "Mission" in output
    assert "TX" in output
    assert "Chicago" in output
    assert "IL" in output


def test_print_step_panel_marks_completed_steps() -> None:
    from global_entry_scanner.display import print_step_panel

    test_con = _test_console()
    with mock.patch("global_entry_scanner.display.console", test_con):
        print_step_panel(current=3)

    output = test_con.file.getvalue()  # type: ignore[union-attr]
    assert "Select Locations" in output
    assert "Notification Channels" in output
    assert "Configure Channels" in output
    assert "Confirm & Save" in output
    assert "✓" in output  # completed steps marker
    assert "●" in output  # current step marker
    assert "○" in output  # upcoming step marker


def test_print_summary_panel_shows_locations_and_channels() -> None:
    from global_entry_scanner.display import print_summary_panel

    test_con = _test_console()
    with mock.patch("global_entry_scanner.display.console", test_con):
        print_summary_panel(
            locations=["San Francisco, CA", "Los Angeles, CA"],
            channels=["email", "discord"],
        )

    output = test_con.file.getvalue()  # type: ignore[union-attr]
    assert "San Francisco, CA" in output
    assert "Los Angeles, CA" in output
    assert "email" in output
    assert "discord" in output


def test_make_scan_renderable_shows_location_and_status() -> None:
    from global_entry_scanner.display import make_scan_renderable

    results = [
        ScanResult(location_id=5001, city="Mission", new_appointments=[], error=None),
    ]
    renderable = make_scan_renderable(
        results=results,
        events=["14:32:01  Scan OK — no new slots"],
        last_check=datetime(2026, 4, 29, 14, 32, 0),
        next_check_in=840,
        active=True,
    )
    buf = StringIO()
    Console(file=buf, no_color=True, width=200).print(renderable)
    output = buf.getvalue()
    assert "Mission" in output
    assert "OK" in output
    assert "14:32:01" in output


def test_make_scan_renderable_shows_error_status() -> None:
    from global_entry_scanner.display import make_scan_renderable

    results = [
        ScanResult(
            location_id=5001, city="Mission", new_appointments=[], error="Connection refused"
        ),
    ]
    renderable = make_scan_renderable(
        results=results,
        events=[],
        last_check=None,
        next_check_in=0,
        active=True,
    )
    buf = StringIO()
    Console(file=buf, no_color=True, width=200).print(renderable)
    output = buf.getvalue()
    assert "Connection refused" in output
    assert "Mission" in output
