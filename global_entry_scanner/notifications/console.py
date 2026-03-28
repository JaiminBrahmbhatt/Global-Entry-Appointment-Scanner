from __future__ import annotations


class ConsoleNotifier:
    """Prints notifications directly to stdout. No credentials required."""

    def validate(self) -> None:
        pass

    def send(self, subject: str, message: str) -> None:
        print(f"\n*** {subject} ***\n{message}\n")
