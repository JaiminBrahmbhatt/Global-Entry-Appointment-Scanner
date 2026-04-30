from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from pathlib import Path

import click
import questionary

from global_entry_scanner.config import (
    Config,
    DiscordConfig,
    EmailConfig,
    LocationsConfig,
    NotificationConfig,
    ScannerConfig,
    SlackConfig,
    SMSConfig,
    load_config,
    save_config,
)
from global_entry_scanner.notifications.console import ConsoleNotifier
from global_entry_scanner.notifications.discord import DiscordNotifier
from global_entry_scanner.notifications.email import EmailNotifier
from global_entry_scanner.notifications.slack import SlackNotifier
from global_entry_scanner.notifications.sms import SMSNotifier
from global_entry_scanner.scanner import Scanner

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def _config_path() -> Path:
    env = os.environ.get("GES_CONFIG_PATH")
    return Path(env) if env else Path.home() / ".config" / "global-entry-scanner" / "config.toml"


@click.group()
def cli() -> None:
    """Global Entry Appointment Scanner — find open slots and get notified."""


@cli.command()
def locations() -> None:
    """List all available Global Entry enrollment locations."""
    from global_entry_scanner.display import console, print_locations_table

    scanner = Scanner(location_ids=[])
    locs = scanner.fetch_locations()
    if not locs:
        console.print("[red]Failed to fetch locations.[/red]")
        raise SystemExit(1)
    print_locations_table(locs)


@cli.command()
def setup() -> None:
    """Interactive setup wizard. Saves config to ~/.config/global-entry-scanner/config.toml"""
    from global_entry_scanner.display import console, print_step_panel, print_summary_panel

    # Step 1: Select Locations
    print_step_panel(1)
    console.print("Fetching available locations...")
    scanner = Scanner(location_ids=[])
    all_locs = scanner.fetch_locations()
    if not all_locs:
        console.print("[red]Could not fetch locations. Check your network connection.[/red]")
        raise SystemExit(1)

    choices = [
        questionary.Choice(title=f"{loc.city}, {loc.state} — {loc.name}", value=loc.id)
        for loc in sorted(all_locs.values(), key=lambda x: x.city)
    ]
    selected_ids: list[int] = questionary.checkbox(
        "Select locations to monitor (type to search, space to select, enter to confirm):",
        choices=choices,
        use_search_filter=True,
        use_jk_keys=False,
    ).ask()

    if not selected_ids:
        console.print("[red]No locations selected. Exiting.[/red]")
        raise SystemExit(1)

    # Step 2: Notification Channels
    print_step_panel(2)
    channel_choices = ["console", "email", "discord", "slack", "sms"]
    selected_channels: list[str] = questionary.checkbox(
        "Which notification channels do you want to enable? (console is enabled by default)",
        choices=channel_choices,
    ).ask() or []

    if not selected_channels:
        selected_channels = ["console"]

    # Step 3: Configure Each Channel
    print_step_panel(3)
    discord_cfg: DiscordConfig | None = None
    slack_cfg: SlackConfig | None = None
    email_cfg: EmailConfig | None = None
    sms_cfg: SMSConfig | None = None

    def _ask_required(prompt: str, password: bool = False) -> str:
        """Prompt until the user enters a non-empty value."""
        while True:
            answer = (questionary.password(prompt) if password else questionary.text(prompt)).ask()
            if answer is None:
                console.print("[yellow]Aborted.[/yellow]")
                raise SystemExit(1)
            if answer:
                return str(answer)
            console.print("[red]This field is required.[/red]")

    if "discord" in selected_channels:
        url = _ask_required("Discord webhook URL:")
        discord_cfg = DiscordConfig(webhook_url=url)

    if "slack" in selected_channels:
        url = _ask_required("Slack webhook URL:")
        slack_cfg = SlackConfig(webhook_url=url)

    if "email" in selected_channels:
        from global_entry_scanner.notifications.email import SMTP_PROVIDERS

        provider = questionary.select(
            "Email provider:",
            choices=list(SMTP_PROVIDERS.keys()),
        ).ask()

        preset_host, preset_port, password_hint = SMTP_PROVIDERS[provider]

        if preset_host is None:
            smtp_host = _ask_required("SMTP host (e.g. smtp.example.com):")
            smtp_port = int(questionary.text("SMTP port:", default="587").ask())
        else:
            smtp_host = preset_host
            smtp_port = preset_port if preset_port is not None else 587

        from_email = _ask_required("From email address:")
        to_email = _ask_required("To email address:")
        password = _ask_required(f"{password_hint}:", password=True)
        email_cfg = EmailConfig(
            from_email=from_email,
            to_email=to_email,
            password=password,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
        )

    if "sms" in selected_channels:
        account_sid = _ask_required("Twilio Account SID:")
        auth_token = _ask_required("Twilio Auth Token:", password=True)
        to_number = _ask_required("To phone number (e.g. +12125551234):")
        from_number = _ask_required("From Twilio number (e.g. +12125550000):")
        sms_cfg = SMSConfig(
            account_sid=account_sid,
            auth_token=auth_token,
            to_number=to_number,
            from_number=from_number,
        )

    # Step 4: Confirm & Save
    print_step_panel(4)
    location_names = [
        f"{all_locs[i].city}, {all_locs[i].state}"
        for i in selected_ids
        if i in all_locs
    ]
    print_summary_panel(location_names, selected_channels)

    cfg = Config(
        locations=LocationsConfig(ids=selected_ids),
        scanner=ScannerConfig(),
        notifications=NotificationConfig(
            discord=discord_cfg,
            slack=slack_cfg,
            email=email_cfg,
            sms=sms_cfg,
            console="console" in selected_channels,
        ),
    )
    save_config(cfg, _config_path())
    console.print(f"[bold green]✓ Config saved to {_config_path()}[/bold green]")


@cli.command()
@click.option(
    "--locations",
    "location_names",
    default=None,
    help="Comma-separated city names (overrides config)",
)
@click.option(
    "--notify",
    "notify_channels",
    default=None,
    help="Comma-separated channels: email,discord,slack,sms",
)
def scan(location_names: str | None, notify_channels: str | None) -> None:
    """Run the appointment scanner using saved config."""
    from rich.live import Live

    from global_entry_scanner.display import console, make_scan_renderable
    from global_entry_scanner.models import ScanResult

    try:
        cfg = load_config(_config_path())
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)

    location_ids = cfg.locations.ids
    if location_names:
        s = Scanner(location_ids=[])
        all_locs = s.fetch_locations()
        by_city = {loc.city.lower(): loc.id for loc in all_locs.values()}
        location_ids = [
            by_city[name.strip().lower()]
            for name in location_names.split(",")
            if name.strip().lower() in by_city
        ]
        if not location_ids:
            console.print("[red]No matching locations found.[/red]")
            raise SystemExit(1)

    scanner = Scanner(
        location_ids=location_ids,
        check_interval=cfg.scanner.check_interval,
        error_interval=cfg.scanner.error_interval,
        limit=cfg.scanner.limit,
    )

    active_channels = (
        set(notify_channels.split(","))
        if notify_channels
        else {"console", "email", "discord", "slack", "sms"}
    )

    if cfg.notifications.console and "console" in active_channels:
        scanner.add_notifier(ConsoleNotifier())
    if cfg.notifications.discord and "discord" in active_channels:
        scanner.add_notifier(DiscordNotifier(webhook_url=cfg.notifications.discord.webhook_url))
    if cfg.notifications.slack and "slack" in active_channels:
        scanner.add_notifier(SlackNotifier(webhook_url=cfg.notifications.slack.webhook_url))
    if cfg.notifications.email and "email" in active_channels:
        email_cfg = cfg.notifications.email
        scanner.add_notifier(
            EmailNotifier(
                from_email=email_cfg.from_email,
                to_email=email_cfg.to_email,
                password=email_cfg.password,
                smtp_host=email_cfg.smtp_host,
                smtp_port=email_cfg.smtp_port,
            )
        )
    if cfg.notifications.sms and "sms" in active_channels:
        s_cfg = cfg.notifications.sms
        scanner.add_notifier(
            SMSNotifier(
                account_sid=s_cfg.account_sid,
                auth_token=s_cfg.auth_token,
                to_number=s_cfg.to_number,
                from_number=s_cfg.from_number,
            )
        )

    try:
        scanner.validate_notifiers()
    except ValueError as e:
        from rich.panel import Panel
        console.print(Panel(f"[red]{e}[/red]", title="[red]Configuration Error[/red]"))
        raise SystemExit(1)

    results: list[ScanResult] = []
    events: list[str] = []
    last_check: datetime | None = None
    check_interval = cfg.scanner.check_interval
    error_interval = cfg.scanner.error_interval

    with Live(
        make_scan_renderable(results, events, last_check, 0, True),
        refresh_per_second=4,
        console=console,
    ) as live:
        try:
            while True:
                results = scanner.check_once()
                last_check = datetime.now()

                has_error = any(r.error for r in results)
                new_results = [r for r in results if r.new_appointments]

                if new_results:
                    total = sum(len(r.new_appointments) for r in new_results)
                    subject = (
                        f"Global Entry: {total} new slot{'s' if total != 1 else ''} available"
                    )
                    message_lines: list[str] = []
                    for r in new_results:
                        message_lines.append(f"{r.city}:")
                        for appt in r.new_appointments:
                            message_lines.append(f"  • {appt.start.strftime('%Y-%m-%d %H:%M')}")
                        events.append(
                            f"{datetime.now().strftime('%H:%M:%S')}  "
                            f"{len(r.new_appointments)} new slot(s) at {r.city}"
                        )
                    scanner.notify_all(subject, "\n".join(message_lines))
                else:
                    events.append(
                        f"{datetime.now().strftime('%H:%M:%S')}  Scan OK — no new slots"
                    )

                events = events[-10:]
                interval = error_interval if has_error else check_interval

                for remaining in range(interval, 0, -1):
                    live.update(
                        make_scan_renderable(results, events, last_check, remaining, True)
                    )
                    time.sleep(1)
        except KeyboardInterrupt:
            pass

    console.print("[bold green]Scanner stopped.[/bold green]")


@cli.command("mcp")
def mcp_command() -> None:
    """Start the MCP server for AI agent integration."""
    from global_entry_scanner.mcp_server import app

    app.run()
