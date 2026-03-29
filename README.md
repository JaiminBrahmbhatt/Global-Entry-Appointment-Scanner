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

```bash
# macOS
brew install pipx

# Linux
sudo apt install pipx       # Debian / Ubuntu
sudo dnf install pipx       # Fedora

# Windows
scoop install pipx          # or: winget install pipx

pipx install global-entry-scanner
```

> Inside a virtual environment? `pip install global-entry-scanner` works too.

## Quick start

```bash
global-entry-scanner setup   # pick locations + notification channels
global-entry-scanner scan    # start watching
```

## CLI

```bash
global-entry-scanner locations                          # list all enrollment centers
global-entry-scanner scan --locations "Chicago, Dallas" # override locations
global-entry-scanner scan --notify email,slack          # override channels
global-entry-scanner mcp                                # start MCP server
```

## MCP server

Works with Claude Desktop, Cursor, Windsurf, Gemini CLI, VS Code, and any MCP-compatible tool.

```bash
pipx install global-entry-scanner
global-entry-scanner mcp
```

Add to your AI tool's MCP config (see [MCP Server wiki page](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/MCP-Server) for per-tool file paths):

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

## Claude Code skill

Ask Claude to find slots, set up monitoring, or configure notifications in plain English — no commands needed.

```
/plugin marketplace add JaiminBrahmbhatt/Global-Entry-Appointment-Scanner
/plugin install global-entry-scanner@global-entry-scanner
```

## Wiki

Full documentation lives in the [wiki](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki):

- [Installation](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/Installation)
- [Quick Start](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/Quick-Start)
- [Configuration](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/Configuration)
- [Notification Channels](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/Notification-Channels) — Email, Discord, Slack, SMS setup
- [CLI Reference](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/CLI-Reference)
- [Python API](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/Python-API)
- [MCP Server](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/MCP-Server)
- [Claude Code Skill](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/Claude-Code-Skill)
- [Developer Guide](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/wiki/Developer-Guide)

## Credits

Inspired by:
- https://gist.github.com/serg06/ac46defe2d9f568ac39665bd50d2e1b1
- https://gist.github.com/clay584/bcbbe3803ca6414ce09426a2c3d4abfb
