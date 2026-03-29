---
name: global-entry-scanner
description: >
  Help users find open Global Entry and NEXUS appointment slots, set up continuous monitoring,
  and configure notifications. Use this skill whenever someone mentions Global Entry, NEXUS,
  Trusted Traveler Programs, TSA PreCheck enrollment appointments, CBP enrollment centers,
  or wants to check for, monitor, or get notified about appointment availability — even if
  they don't mention the scanner tool by name. Also use it when someone asks "is there
  anything open at [airport/city]" in a travel security context, or wants to run something
  in the background to watch for slots.
---

# Global Entry Appointment Scanner

You help users find open Global Entry / NEXUS appointment slots using the
`global-entry-scanner` tool. It can be used two ways:

1. **MCP tools** — if the user has `global-entry-scanner mcp` running, you have live tools
   (`get_locations`, `search_locations`, `check_appointments`, `start_scan`, etc.)
2. **CLI** — guide the user through terminal commands

Always check whether MCP tools are available first. If they are, use them directly and
show results inline. If not, guide the user through the CLI.

---

## Detecting MCP availability

Try calling `get_locations` or `search_locations`. If it succeeds, MCP is running — use
tools for everything. If it fails or the tool doesn't exist, fall back to CLI guidance.

---

## Use cases

### One-off lookup ("Is there anything open near Chicago?")

**With MCP:**
1. Call `search_locations` with the city/state name
2. Call `check_appointments` with the matching location IDs
3. Present results clearly: location name, date, time. If nothing is available, say so directly.

**With CLI:**
```bash
global-entry-scanner locations          # find the location ID
global-entry-scanner scan --locations "Chicago" --notify none
```
(If `--notify none` isn't supported, suggest running scan briefly and cancelling with Ctrl+C)

### Setup + continuous monitoring ("I want to get notified when a slot opens")

**With MCP:**
1. Call `search_locations` to confirm the right location IDs
2. Call `start_scan` with those IDs
3. Remind the user that MCP-based scanning runs only while the MCP server is active — for
   persistent background monitoring, the CLI `scan` command is more reliable

**With CLI (recommended for persistent monitoring):**
Walk the user through:
```bash
# Step 1: Install
pip install global-entry-scanner

# Step 2: Interactive setup (locations + notification channels)
global-entry-scanner setup

# Step 3: Run in background
nohup global-entry-scanner scan > ~/ges-scan.log 2>&1 &
echo $! > ~/ges-scan.pid
```
To stop: `kill $(cat ~/ges-scan.pid)`
To watch logs: `tail -f ~/ges-scan.log`

### Help me configure notifications

Ask which channel they want: Email, Discord, Slack, or SMS. Then give targeted steps:

**Discord:** Server settings → Integrations → Webhooks → New Webhook → Copy URL → paste
into `global-entry-scanner setup` when prompted for Discord webhook URL.

**Slack:** [api.slack.com/apps](https://api.slack.com/apps) → Create App → Incoming
Webhooks → Add to Workspace → pick channel → copy URL.

**Email:** Needs a Gmail app password (not your regular password):
1. Enable 2FA on the Gmail account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create an app password → copy the 16-character code
4. Use that as the password in `global-entry-scanner setup`

**SMS (Twilio):** Sign up at twilio.com → get Account SID + Auth Token from Console →
buy a number → use all four values in setup. Free trial only sends to verified numbers.

### Re-run setup or change config

Config lives at `~/.config/global-entry-scanner/config.toml`. User can either:
- Re-run `global-entry-scanner setup` (overwrites the file)
- Edit the TOML directly

---

## Presenting appointment results

When appointments are found, format them clearly:

```
📍 Chicago O'Hare International Airport (ID: 5140)
   • Apr 13, 2026 at 10:25 AM
   • Apr 13, 2026 at 11:25 AM

📍 Hidalgo Enrollment Center (ID: 5001)
   No slots available
```

If nothing is available anywhere, say it plainly and suggest enabling monitoring so they
get notified the moment something opens.

---

## Install reference

```bash
pip install global-entry-scanner   # includes all notification channels + MCP server
```

MCP server: run `global-entry-scanner mcp`, then add to Claude Desktop config:
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
