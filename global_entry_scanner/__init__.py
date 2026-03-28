"""
global-entry-scanner — scan for Global Entry appointment slots and get notified.

Quick start:
    from global_entry_scanner import Scanner
    from global_entry_scanner.notifications import SlackNotifier

    scanner = Scanner(location_ids=[5001, 5140])
    scanner.add_notifier(SlackNotifier(webhook_url="https://hooks.slack.com/..."))
    scanner.start()
"""

from global_entry_scanner.config import Config, load_config, save_config
from global_entry_scanner.models import Appointment, Location, ScanResult
from global_entry_scanner.notifications import (
    DiscordNotifier,
    EmailNotifier,
    Notifier,
    SMSNotifier,
    SlackNotifier,
)
from global_entry_scanner.scanner import Scanner

__all__ = [
    "Scanner",
    "Config",
    "load_config",
    "save_config",
    "Location",
    "Appointment",
    "ScanResult",
    "Notifier",
    "EmailNotifier",
    "DiscordNotifier",
    "SlackNotifier",
    "SMSNotifier",
]
