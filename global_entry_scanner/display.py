from __future__ import annotations

from datetime import datetime

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from global_entry_scanner.models import Location, ScanResult

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


SETUP_STEPS = [
    "Select Locations",
    "Notification Channels",
    "Configure Channels",
    "Confirm & Save",
]


def print_step_panel(current: int) -> None:
    """Print setup wizard progress panel. current is 1-based."""
    lines = []
    for i, step in enumerate(SETUP_STEPS, start=1):
        if i < current:
            marker = "[bold green]✓[/bold green]"
        elif i == current:
            marker = "[bold cyan]●[/bold cyan]"
        else:
            marker = "[dim]○[/dim]"
        lines.append(f"  {marker}  {i}. {step}")
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold]Global Entry Scanner Setup[/bold]",
            border_style="cyan",
        )
    )


def print_summary_panel(locations: list[str], channels: list[str]) -> None:
    """Print a summary of the collected config before saving."""
    channel_str = ", ".join(channels) if channels else "console"
    lines = [
        f"  [bold]Locations:[/bold]  {', '.join(locations)}",
        f"  [bold]Channels:[/bold]   {channel_str}",
    ]
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold green]Configuration Summary[/bold green]",
            border_style="green",
        )
    )


def make_scan_renderable(
    results: list[ScanResult],
    events: list[str],
    last_check: datetime | None,
    next_check_in: int,
    active: bool,
) -> Panel:
    """Build the live scan display panel. Safe to call with empty results."""
    status_str = "[bold green]Running ●[/bold green]" if active else "[bold red]Stopped[/bold red]"

    if last_check is not None:
        elapsed = int((datetime.now() - last_check).total_seconds())
        mins, secs = divmod(next_check_in, 60)
        header_str = f"Last check: {elapsed}s ago  |  Next check in: {mins}m {secs:02d}s"
    else:
        header_str = "Starting..."

    table = Table(show_header=True, header_style="bold", box=box.SIMPLE, show_edge=False)
    table.add_column("Location", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("New Slots", justify="right")

    for r in results:
        if r.error:
            truncated = r.error[:40] + "…" if len(r.error) > 40 else r.error
            status_cell = f"✗ {truncated}"
            slots_cell = ""
        else:
            status_cell = "✓ OK"
            slots_cell = str(len(r.new_appointments)) if r.new_appointments else "0"
        table.add_row(r.city, status_cell, slots_cell)

    events_text = "\n".join(events) if events else "No events yet"
    events_panel = Panel(events_text, title="Recent Events", border_style="dim")

    content = Group(Text(header_str), table, events_panel)
    return Panel(
        content,
        title=f"[bold]Global Entry Scanner[/bold] — {status_str}",
        border_style="cyan",
    )
