from __future__ import annotations

import logging
import os
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
    scanner = Scanner(location_ids=[])
    locs = scanner.fetch_locations()
    if not locs:
        click.echo("Failed to fetch locations.")
        raise SystemExit(1)
    for loc in sorted(locs.values(), key=lambda x: (x.state, x.city)):
        click.echo(f"  {loc.id:>6}  {loc.city}, {loc.state}  ({loc.name})")


@cli.command()
def setup() -> None:
    """Interactive setup wizard. Saves config to ~/.config/global-entry-scanner/config.toml"""
    click.echo("Fetching available locations...")
    scanner = Scanner(location_ids=[])
    all_locs = scanner.fetch_locations()
    if not all_locs:
        click.echo("Could not fetch locations. Check your network connection.")
        raise SystemExit(1)

    choices = [
        questionary.Choice(title=f"{loc.city}, {loc.state} — {loc.name}", value=loc.id)
        for loc in sorted(all_locs.values(), key=lambda x: x.city)
    ]
    selected_ids: list[int] = questionary.checkbox(
        "Select locations to monitor (type to search, space to select, enter to confirm):",
        choices=choices,
        use_search_filter=True,
    ).ask()

    if not selected_ids:
        click.echo("No locations selected. Exiting.")
        raise SystemExit(1)

    channel_choices = ["console", "email", "discord", "slack", "sms"]
    selected_channels: list[str] = questionary.checkbox(
        "Which notification channels do you want to enable? (console is enabled by default)",
        choices=channel_choices,
    ).ask() or []

    if not selected_channels:
        selected_channels = ["console"]

    discord_cfg: DiscordConfig | None = None
    slack_cfg: SlackConfig | None = None
    email_cfg: EmailConfig | None = None
    sms_cfg: SMSConfig | None = None

    if "discord" in selected_channels:
        url = questionary.text("Discord webhook URL:").ask()
        discord_cfg = DiscordConfig(webhook_url=url)

    if "slack" in selected_channels:
        url = questionary.text("Slack webhook URL:").ask()
        slack_cfg = SlackConfig(webhook_url=url)

    if "email" in selected_channels:
        from_email = questionary.text("From email address:").ask()
        to_email = questionary.text("To email address:").ask()
        password = questionary.password("Gmail app password:").ask()
        email_cfg = EmailConfig(from_email=from_email, to_email=to_email, password=password)

    if "sms" in selected_channels:
        account_sid = questionary.text("Twilio Account SID:").ask()
        auth_token = questionary.password("Twilio Auth Token:").ask()
        to_number = questionary.text("To phone number (e.g. +12125551234):").ask()
        from_number = questionary.text("From Twilio number (e.g. +12125550000):").ask()
        sms_cfg = SMSConfig(
            account_sid=account_sid,
            auth_token=auth_token,
            to_number=to_number,
            from_number=from_number,
        )

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
    click.echo(f"Config saved to {_config_path()}")


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
    try:
        cfg = load_config(_config_path())
    except FileNotFoundError as e:
        click.echo(str(e))
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
            click.echo("No matching locations found.")
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

    scanner.start()


@cli.command("mcp")
def mcp_command() -> None:
    """Start the MCP server for AI agent integration."""
    try:
        from global_entry_scanner.mcp_server import app
    except ImportError as e:
        click.echo("MCP support not installed. Run: pip install global-entry-scanner[mcp]")
        raise SystemExit(1) from e
    app.run()
