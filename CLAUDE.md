# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Before every commit

Always run these three checks before committing. All must pass:

```bash
ruff check global_entry_scanner/ tests/
mypy global_entry_scanner/
pytest
```

## Commands

```bash
# Install for development (all extras + dev tools)
pip install -e ".[all,dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_scanner.py -v

# Run a single test
pytest tests/test_scanner.py::test_check_once_deduplicates -v

# Run live API tests (skipped in CI by default)
pytest -m integration

# Lint
ruff check .

# Type check
mypy global_entry_scanner/
```

## Architecture

### Package layout

```
global_entry_scanner/
├── models.py          # Location, Appointment (frozen dataclasses), ScanResult
├── config.py          # Config dataclasses + load_config/save_config (TOML)
├── scanner.py         # Scanner class — core poll loop, API fetching, deduplication
├── notifications/
│   ├── base.py        # Notifier protocol (send + validate)
│   ├── email.py       # Gmail SMTP
│   ├── discord.py     # Discord webhook
│   ├── slack.py       # Slack webhook
│   └── sms.py         # Twilio (optional dep, graceful ImportError fallback)
├── cli.py             # Click CLI (setup, scan, locations, mcp commands)
└── mcp_server.py      # FastMCP server (optional [mcp] extra)
```

### Key design decisions

**`Notifier` is a structural Protocol** (`runtime_checkable`) — notifiers do not inherit from a base class. Any object with `send(subject, message)` and `validate()` qualifies.

**`Scanner._seen`** is an in-memory `dict[int, set[str]]` (location_id → set of `startTimestamp` ISO strings). Deduplication resets on restart intentionally — slots change frequently and re-notifying after restart is acceptable.

**`_locations_cache`** is a module-level `TTLCache` (15-day TTL, maxsize=1, key `"all"`). Tests clear it via an autouse fixture in `conftest.py` — if you add tests that call `fetch_locations`, that fixture handles isolation automatically.

**`Scanner._get()`** retries up to 3 times with exponential backoff on 5xx/network errors. It raises immediately on 4xx. `fetch_appointments` only catches 404 (returns `[]`); all other errors propagate to `check_once` which records them in `ScanResult.error`.

**Concurrent notifications** — `_notify_all()` uses `ThreadPoolExecutor`. Failures are logged per-channel and never re-raised.

**Optional deps** — `sms.py` does a top-level `try/except ImportError` for `twilio`. `mcp_server.py` is only imported when `mcp` extra is installed. Both modules have per-module `warn_unused_ignores = false` mypy overrides in `pyproject.toml` because the except branches are unreachable when the deps are installed.

### Config

Saved to `~/.config/global-entry-scanner/config.toml`. Override path via `GES_CONFIG_PATH` env var (used in tests). `load_config` raises `FileNotFoundError` if the file doesn't exist — `scan` command catches this and prints a helpful message.

### CI

- `ci.yml` — ruff + mypy + pytest on Python 3.10/3.11/3.12
- `pylint.yml` — ruff check only (legacy name kept)
- `publish.yml` — PyPI Trusted Publisher (OIDC), triggers on GitHub Release creation
