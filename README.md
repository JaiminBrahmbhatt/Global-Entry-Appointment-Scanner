# Global Entry Appointment Scanner

Scan for open Global Entry / NEXUS appointment slots and get notified the moment one appears.

[![CI](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/global-entry-scanner)](https://pypi.org/project/global-entry-scanner/)
[![Python](https://img.shields.io/pypi/pyversions/global-entry-scanner)](https://pypi.org/project/global-entry-scanner/)

## Install

```bash
pip install global-entry-scanner           # core (email only)
pip install global-entry-scanner[slack]    # + Slack
pip install global-entry-scanner[discord]  # + Discord
pip install global-entry-scanner[sms]      # + Twilio SMS
pip install global-entry-scanner[mcp]      # + MCP server for AI agents
pip install global-entry-scanner[all]      # everything
```

## Quick start

```bash
# 1. Interactive setup — pick locations and configure notifications
global-entry-scanner setup

# 2. Run the scanner
global-entry-scanner scan
```

## CLI

```bash
global-entry-scanner locations                                    # list all enrollment centers
global-entry-scanner setup                                        # interactive config wizard
global-entry-scanner scan                                         # run with saved config
global-entry-scanner scan --locations "Chicago, Dallas"           # override locations
global-entry-scanner scan --notify email,slack                    # override channels
global-entry-scanner mcp                                          # start MCP server
```

Config is saved to `~/.config/global-entry-scanner/config.toml`.

## Python API

```python
from global_entry_scanner import Scanner
from global_entry_scanner.notifications import SlackNotifier, DiscordNotifier, EmailNotifier

scanner = Scanner(location_ids=[5001, 5140])
scanner.add_notifier(SlackNotifier(webhook_url="https://hooks.slack.com/..."))
scanner.add_notifier(DiscordNotifier(webhook_url="https://discord.com/api/webhooks/..."))
scanner.add_notifier(EmailNotifier(from_email="you@gmail.com", to_email="you@gmail.com", password="app-password"))
scanner.start()  # blocking; Ctrl+C to stop
```

`Scanner` options:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `location_ids` | required | List of enrollment center IDs |
| `check_interval` | `900` | Seconds between polls (no errors) |
| `error_interval` | `60` | Seconds between polls (on error) |
| `limit` | `5` | Max appointments to fetch per location |

## Notification channels

| Channel | Extra | Credentials |
|---------|-------|-------------|
| Email | _(core)_ | Gmail address + app password |
| Discord | `[discord]` | Webhook URL |
| Slack | `[slack]` | Webhook URL |
| SMS | `[sms]` | Twilio account SID, auth token, phone numbers |

All configured channels fire concurrently. One failing channel does not block the others.

### Discord webhook setup

1. Open your Discord server → go to the channel you want notifications in
2. Click **Edit Channel** (gear icon) → **Integrations** → **Webhooks** → **New Webhook**
3. Give it a name, optionally set an avatar, then click **Copy Webhook URL**
4. Paste the URL into `setup` when prompted, or add it to your config:

```toml
[notifications.discord]
webhook_url = "https://discord.com/api/webhooks/1234567890/xxxx"
```

### Slack webhook setup

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Under **Add features and functionality**, choose **Incoming Webhooks** → toggle it on
3. Click **Add New Webhook to Workspace**, pick a channel, and click **Allow**
4. Copy the webhook URL that appears, then paste it into `setup` when prompted or add it to your config:

```toml
[notifications.slack]
webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/xxxx"
```

## MCP server

Install with `pip install global-entry-scanner[mcp]`, then run `global-entry-scanner mcp`.

Exposes six tools to AI agents: `get_locations`, `search_locations`, `check_appointments`, `start_scan`, `stop_scan`, `get_scan_status`.

**Claude Desktop (`claude_desktop_config.json`):**

```json
{
  "mcpServers": {
    "global-entry-scanner": {
      "command": "global-entry-scanner",
      "args": ["mcp"]
    }
  }
}
```

## Configuration file

`~/.config/global-entry-scanner/config.toml`

```toml
[scanner]
check_interval = 900
error_interval = 60
limit = 5

[locations]
ids = [5001, 5140]

[notifications.discord]
webhook_url = "https://discord.com/api/webhooks/..."

[notifications.slack]
webhook_url = "https://hooks.slack.com/..."

[notifications.email]
from_email = "you@gmail.com"
to_email = "you@gmail.com"
password = "app-password"

[notifications.sms]
account_sid = "..."
auth_token = "..."
to_number = "+12125551234"
from_number = "+12125550000"
```

## Development

```bash
git clone https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner
cd Global-Entry-Appointment-Scanner
pip install -e ".[all,dev]"

# Run tests
pytest

# Run live API tests
pytest -m integration

# Lint + type check
ruff check .
mypy global_entry_scanner/
```

## Credits

Inspired by:
- https://gist.github.com/serg06/ac46defe2d9f568ac39665bd50d2e1b1
- https://gist.github.com/clay584/bcbbe3803ca6414ce09426a2c3d4abfb
