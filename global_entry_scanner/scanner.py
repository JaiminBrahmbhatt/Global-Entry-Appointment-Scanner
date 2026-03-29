from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

import requests
from cachetools import TTLCache

from global_entry_scanner.models import Appointment, Location, ScanResult
from global_entry_scanner.notifications.base import Notifier

logger = logging.getLogger(__name__)

LOCATIONS_API_URL = (
    "https://ttp.cbp.dhs.gov/schedulerapi/locations/?"
    "temporary=false&inviteOnly=false&operational=true&serviceName=Global+Entry"
)
APPOINTMENTS_API_URL = (
    "https://ttp.cbp.dhs.gov/schedulerapi/slots?orderBy=soonest&limit={}&locationId={}&minimum={}"
)

_locations_cache: TTLCache[str, dict[int, Location]] = TTLCache(maxsize=1, ttl=15 * 24 * 60 * 60)


class Scanner:
    def __init__(
        self,
        location_ids: list[int],
        check_interval: int = 900,
        error_interval: int = 60,
        limit: int = 5,
    ) -> None:
        self._location_ids = location_ids
        self._check_interval = check_interval
        self._error_interval = error_interval
        self._limit = limit
        self._notifiers: list[Notifier] = []
        self._seen: dict[int, set[str]] = {}

    def add_notifier(self, notifier: Notifier) -> None:
        self._notifiers.append(notifier)

    # ------------------------------------------------------------------ #
    # API fetching                                                         #
    # ------------------------------------------------------------------ #

    def fetch_locations(self) -> dict[int, Location]:
        """Fetch all Global Entry locations. Result is cached for 15 days."""
        if "all" in _locations_cache:
            return _locations_cache["all"]
        try:
            data = self._get(LOCATIONS_API_URL)
        except Exception as e:
            logger.error("Failed to fetch locations: %s", e)
            return {}
        locations = {
            int(item["id"]): Location(
                id=int(item["id"]),
                name=item["name"],
                city=item["city"].strip(),
                state=item.get("state", ""),
                timezone=item.get("tzData", "UTC"),
            )
            for item in data
        }
        _locations_cache["all"] = locations
        return locations

    def fetch_appointments(self, location_id: int) -> list[Appointment]:
        """Fetch available appointment slots for a location. Returns [] on permanent errors."""
        url = APPOINTMENTS_API_URL.format(self._limit, location_id, 1)
        try:
            data = self._get(url)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                logger.warning("Location %s not found (404)", location_id)
                return []
            raise  # non-404 errors propagate to check_once for error recording
        return [
            Appointment(
                location_id=int(item["locationId"]),
                start=datetime.fromisoformat(item["startTimestamp"]),
                end=datetime.fromisoformat(item["endTimestamp"]),
                active=bool(item["active"]),
            )
            for item in data
        ]

    def _get(self, url: str, max_retries: int = 3) -> Any:
        """GET with exponential backoff. Raises on 4xx (permanent) or after max_retries."""
        last_exc: Exception = RuntimeError("no attempts made")
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                if 400 <= response.status_code < 500:
                    response.raise_for_status()
                response.raise_for_status()
                return response.json()
            except requests.HTTPError as e:
                if e.response is not None and 400 <= e.response.status_code < 500:
                    raise
                last_exc = e
            except requests.RequestException as e:
                last_exc = e
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
        raise last_exc

    # ------------------------------------------------------------------ #
    # Poll loop                                                            #
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        """Start the blocking poll loop. Validates all notifiers first. Ctrl+C to stop."""
        for notifier in self._notifiers:
            notifier.validate()

        logger.info("Starting scanner for %d location(s)...", len(self._location_ids))
        try:
            while True:
                results = self.check_once()
                has_error = any(r.error for r in results)
                new_results = [r for r in results if r.new_appointments]
                if new_results:
                    total = sum(len(r.new_appointments) for r in new_results)
                    subject = (
                        f"Global Entry: {total} new slot{'s' if total != 1 else ''} available"
                    )
                    lines: list[str] = []
                    for result in new_results:
                        lines.append(f"{result.city}:")
                        for appt in result.new_appointments:
                            lines.append(f"  • {appt.start.strftime('%Y-%m-%d %H:%M')}")
                    self._notify_all(subject, "\n".join(lines))
                interval = self._error_interval if has_error else self._check_interval
                logger.info("Next check in %d seconds.", interval)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Scanner stopped.")

    def check_once(self) -> list[ScanResult]:
        """Run a single scan pass across all configured locations. Used by MCP and tests."""
        locations = self.fetch_locations()
        results: list[ScanResult] = []
        for location_id in self._location_ids:
            loc = locations.get(location_id)
            city = loc.city if loc else str(location_id)
            try:
                appointments = self.fetch_appointments(location_id)
                seen = self._seen.setdefault(location_id, set())
                new = [a for a in appointments if a.start.isoformat() not in seen]
                for appt in new:
                    seen.add(appt.start.isoformat())
                results.append(ScanResult(location_id=location_id, city=city, new_appointments=new))
            except Exception as e:
                logger.error("Error scanning location %s: %s", location_id, e)
                results.append(ScanResult(location_id=location_id, city=city, error=str(e)))
        return results

    # ------------------------------------------------------------------ #
    # Notifications                                                        #
    # ------------------------------------------------------------------ #

    def _notify_all(self, subject: str, message: str) -> None:
        """Fire all notifiers concurrently. Logs failures but does not raise."""
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(n.send, subject, message): type(n).__name__
                for n in self._notifiers
            }
            for future, name in futures.items():
                try:
                    future.result()
                except Exception as e:
                    logger.error("Notifier %s failed: %s", name, e)
