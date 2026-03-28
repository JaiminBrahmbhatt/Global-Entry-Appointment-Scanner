from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Notifier(Protocol):
    def send(self, subject: str, message: str) -> None: ...
    def validate(self) -> None: ...
