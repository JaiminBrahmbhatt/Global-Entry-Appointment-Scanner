# Global Entry Appointment Scanner

Scan for open Global Entry / NEXUS appointment slots and get notified the moment one appears.

[![CI](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/global-entry-scanner)](https://pypi.org/project/global-entry-scanner/)

### Works with

[![Claude](https://img.shields.io/badge/Claude-Desktop%20%7C%20Code-black?logo=anthropic)](https://claude.ai)
[![Cursor](https://img.shields.io/badge/Cursor-MCP-black?logo=cursor)](https://cursor.sh)
[![Windsurf](https://img.shields.io/badge/Windsurf-MCP-black)](https://windsurf.ai)
[![Gemini CLI](https://img.shields.io/badge/Gemini%20CLI-MCP-black?logo=google)](https://github.com/google-gemini/gemini-cli)
[![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-MCP-black?logo=github)](https://github.com/features/copilot)
[![VS Code](https://img.shields.io/badge/VS%20Code-MCP-black?logo=visualstudiocode)](https://code.visualstudio.com)

![demo](docs/demo.gif)

## Install

**Recommended — pipx** (installs CLI tools in isolated environments, no conflicts):

```bash
brew install pipx        # macOS
pipx install global-entry-scanner           # core (email only)
pipx install "global-entry-scanner[slack]"  # + Slack
pipx install "global-entry-scanner[discord]"# + Discord
pipx install "global-entry-scanner[sms]"    # + Twilio SMS
pipx install "global-entry-scanner[mcp]"    # + MCP server for AI agents
pipx install "global-entry-scanner[all]"    # everything
```

> On macOS, avoid using the system `pip3` — it points to Python 3.9 which is too old, and Homebrew's Python will block system-wide installs. `pipx` handles all of this automatically.

**Alternative — pip** (if you're inside a virtual environment):

```bash
pip install global-entry-scanner
pip install "global-entry-scanner[all]"
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

### Twilio SMS setup

1. Sign up at [twilio.com](https://www.twilio.com) (free trial includes a small credit)
2. From the [Twilio Console](https://console.twilio.com) dashboard, copy your **Account SID** and **Auth Token**
3. Go to **Phone Numbers** → **Manage** → **Buy a number** to get a Twilio number to send from (free trial includes one)
4. Add the credentials to your config:

```toml
[notifications.sms]
account_sid = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
auth_token  = "your_auth_token"
from_number = "+12125550000"   # your Twilio number
to_number   = "+12125551234"   # number to notify
```

> **Free trial note:** Twilio trial accounts can only send SMS to verified numbers. Go to **Phone Numbers** → **Manage** → **Verified Caller IDs** to add your personal number.

### Slack webhook setup

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Under **Add features and functionality**, choose **Incoming Webhooks** → toggle it on
3. Click **Add New Webhook to Workspace**, pick a channel, and click **Allow**
4. Copy the webhook URL that appears, then paste it into `setup` when prompted or add it to your config:

```toml
[notifications.slack]
webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/xxxx"
```

## Claude Code skill

This repo ships a skill for [Claude Code](https://claude.ai/code) that lets you ask Claude directly about slot availability, set up monitoring, and configure notifications — without remembering any commands.

### Install the skill

**Option 1: From this repo (available now)**

In Claude Code, run:
```
/plugin marketplace add JaiminBrahmbhatt/Global-Entry-Appointment-Scanner
/plugin install global-entry-scanner@global-entry-scanner
```

**Option 2: Official Anthropic marketplace** *(pending review)*

```
/plugin install global-entry-scanner
```

### What you can ask Claude

Once installed, just talk to Claude naturally:

- *"Are there any open Global Entry slots near Chicago or Dallas?"*
- *"Set this up to text me whenever a slot opens at JFK or Newark"*
- *"How do I hook up the MCP server to Claude Desktop?"*
- *"Run the scanner in the background and notify me on Discord"*

Claude will detect whether the MCP server is running and use it directly, or fall back to guiding you through the CLI.

---

## MCP server

Install with `pip install global-entry-scanner[mcp]`, then run `global-entry-scanner mcp`.

Exposes six tools to AI agents: `get_locations`, `search_locations`, `check_appointments`, `start_scan`, `stop_scan`, `get_scan_status`.

The MCP server works with any MCP-compatible AI tool. The config snippet is the same across all of them — just drop it in the right file.

**Claude Desktop** — `~/Library/Application Support/Claude/claude_desktop_config.json`

**Cursor** — `~/.cursor/mcp.json`

**Windsurf** — `~/.codeium/windsurf/mcp_config.json`

**VS Code (GitHub Copilot)** — `.vscode/mcp.json` in your workspace

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

**Gemini CLI** — add to `~/.gemini/settings.json`:

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
