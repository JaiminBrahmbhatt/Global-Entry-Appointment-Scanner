from __future__ import annotations

from rich import box
from rich.console import Console
from rich.table import Table

from global_entry_scanner.models import Location

console = Console()


def print_locations_table(locations: dict[int, Location]) -> None:
    table = Table(
        title="[bold]Global Entry Locations[/bold]",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED,
    )
    table.add_column("ID", style="dim", justify="right", no_wrap=True)
    table.add_column("City")
    table.add_column("State")
    table.add_column("Name", style="dim")
    for loc in sorted(locations.values(), key=lambda x: (x.state, x.city)):
        table.add_row(str(loc.id), loc.city, loc.state, loc.name)
    console.print(table)
