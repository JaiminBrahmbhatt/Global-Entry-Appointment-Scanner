from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
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
