from __future__ import annotations

import threading
from typing import Any

from mcp.server.fastmcp import FastMCP

from global_entry_scanner.scanner import Scanner

app = FastMCP("global-entry-scanner")

_scanner = Scanner(location_ids=[])
_scan_thread: threading.Thread | None = None
_scan_active = False
_latest_results: list[dict[str, Any]] = []


@app.tool()
def get_locations() -> list[dict[str, Any]]:
    """Return all available Global Entry enrollment locations."""
    locs = _scanner.fetch_locations()
    return [
        {
            "id": loc.id,
            "name": loc.name,
            "city": loc.city,
            "state": loc.state,
            "timezone": loc.timezone,
        }
        for loc in sorted(locs.values(), key=lambda x: (x.state, x.city))
    ]


@app.tool()
def search_locations(query: str) -> list[dict[str, Any]]:
    """Search Global Entry locations by city or state name (case-insensitive substring match)."""
    locs = _scanner.fetch_locations()
    q = query.lower()
    return [
        {"id": loc.id, "name": loc.name, "city": loc.city, "state": loc.state}
        for loc in locs.values()
        if q in loc.city.lower() or q in loc.state.lower() or q in loc.name.lower()
    ]


@app.tool()
def check_appointments(location_ids: list[int]) -> list[dict[str, Any]]:
    """Check available appointment slots for the given location IDs."""
    s = Scanner(location_ids=location_ids)
    results: list[dict[str, Any]] = []
    for loc_id in location_ids:
        appointments = s.fetch_appointments(loc_id)
        results.extend(
            {
                "location_id": a.location_id,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "active": a.active,
            }
            for a in appointments
        )
    return results


@app.tool()
def start_scan(location_ids: list[int]) -> str:
    """Start background polling for the given location IDs."""
    global _scan_thread, _scan_active, _scanner
    if _scan_active:
        return "Scanner is already running."
    _scanner = Scanner(location_ids=location_ids)
    _scan_active = True

    def _run() -> None:
        global _scan_active, _latest_results
        import time

        while _scan_active:
            results = _scanner.check_once()
            _latest_results = [
                {
                    "location_id": r.location_id,
                    "city": r.city,
                    "new_appointments": len(r.new_appointments),
                    "error": r.error,
                }
                for r in results
            ]
            time.sleep(_scanner._check_interval)

    _scan_thread = threading.Thread(target=_run, daemon=True)
    _scan_thread.start()
    return f"Scanner started for location IDs: {location_ids}"


@app.tool()
def stop_scan() -> str:
    """Stop the background scanner."""
    global _scan_active
    _scan_active = False
    return "Scanner stopped."


@app.tool()
def get_scan_status() -> dict[str, Any]:
    """Return the current scanner state and latest found appointments."""
    return {
        "active": _scan_active,
        "location_ids": _scanner._location_ids,
        "latest_results": _latest_results,
    }


if __name__ == "__main__":
    app.run()
