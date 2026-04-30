from __future__ import annotations

from io import StringIO
from unittest import mock

from rich.console import Console

from global_entry_scanner.models import Location


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
