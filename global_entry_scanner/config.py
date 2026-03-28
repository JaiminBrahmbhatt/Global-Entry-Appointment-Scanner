from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-redef]

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "global-entry-scanner" / "config.toml"


@dataclass
class ScannerConfig:
    check_interval: int = 900
    error_interval: int = 60
    limit: int = 5


@dataclass
class LocationsConfig:
    ids: list[int] = field(default_factory=list)


@dataclass
class DiscordConfig:
    webhook_url: str


@dataclass
class SlackConfig:
    webhook_url: str


@dataclass
class EmailConfig:
    from_email: str
    to_email: str
    password: str


@dataclass
class SMSConfig:
    account_sid: str
    auth_token: str
    to_number: str
    from_number: str


@dataclass
class NotificationConfig:
    discord: DiscordConfig | None = None
    slack: SlackConfig | None = None
    email: EmailConfig | None = None
    sms: SMSConfig | None = None


@dataclass
class Config:
    locations: LocationsConfig = field(default_factory=LocationsConfig)
    scanner: ScannerConfig = field(default_factory=ScannerConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)


def load_config(path: Path | None = None) -> Config:
    """Load config from a TOML file. Raises FileNotFoundError if file does not exist."""
    resolved = path if path is not None else DEFAULT_CONFIG_PATH
    if not resolved.exists():
        raise FileNotFoundError(
            f"Config not found at {resolved}. Run `global-entry-scanner setup` first."
        )
    with open(resolved, "rb") as f:
        data: dict[str, Any] = tomllib.load(f)

    scanner_data = data.get("scanner", {})
    scanner = ScannerConfig(
        check_interval=scanner_data.get("check_interval", 900),
        error_interval=scanner_data.get("error_interval", 60),
        limit=scanner_data.get("limit", 5),
    )

    locations = LocationsConfig(ids=data.get("locations", {}).get("ids", []))

    notif_data = data.get("notifications", {})
    discord: DiscordConfig | None = None
    slack: SlackConfig | None = None
    email: EmailConfig | None = None
    sms: SMSConfig | None = None

    if "discord" in notif_data:
        discord = DiscordConfig(webhook_url=notif_data["discord"]["webhook_url"])
    if "slack" in notif_data:
        slack = SlackConfig(webhook_url=notif_data["slack"]["webhook_url"])
    if "email" in notif_data:
        d = notif_data["email"]
        email = EmailConfig(
            from_email=d["from_email"], to_email=d["to_email"], password=d["password"]
        )
    if "sms" in notif_data:
        d = notif_data["sms"]
        sms = SMSConfig(
            account_sid=d["account_sid"],
            auth_token=d["auth_token"],
            to_number=d["to_number"],
            from_number=d["from_number"],
        )

    return Config(
        locations=locations,
        scanner=scanner,
        notifications=NotificationConfig(discord=discord, slack=slack, email=email, sms=sms),
    )


def save_config(cfg: Config, path: Path | None = None) -> None:
    """Serialize Config to TOML and write to disk. Creates parent directories as needed."""
    resolved = path if path is not None else DEFAULT_CONFIG_PATH
    resolved.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines += [
        "[scanner]",
        f"check_interval = {cfg.scanner.check_interval}",
        f"error_interval = {cfg.scanner.error_interval}",
        f"limit = {cfg.scanner.limit}",
        "",
        "[locations]",
        f"ids = {cfg.locations.ids}",
        "",
    ]

    if cfg.notifications.discord:
        lines += [
            "[notifications.discord]",
            f'webhook_url = "{cfg.notifications.discord.webhook_url}"',
            "",
        ]
    if cfg.notifications.slack:
        lines += [
            "[notifications.slack]",
            f'webhook_url = "{cfg.notifications.slack.webhook_url}"',
            "",
        ]
    if cfg.notifications.email:
        e = cfg.notifications.email
        lines += [
            "[notifications.email]",
            f'from_email = "{e.from_email}"',
            f'to_email = "{e.to_email}"',
            f'password = "{e.password}"',
            "",
        ]
    if cfg.notifications.sms:
        s = cfg.notifications.sms
        lines += [
            "[notifications.sms]",
            f'account_sid = "{s.account_sid}"',
            f'auth_token = "{s.auth_token}"',
            f'to_number = "{s.to_number}"',
            f'from_number = "{s.from_number}"',
            "",
        ]

    resolved.write_text("\n".join(lines))
