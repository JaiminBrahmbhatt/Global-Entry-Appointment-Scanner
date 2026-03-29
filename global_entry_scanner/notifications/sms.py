from __future__ import annotations

import logging

from twilio.rest import Client  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class SMSNotifier:
    def __init__(self, account_sid: str, auth_token: str, to_number: str, from_number: str) -> None:
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._to_number = to_number
        self._from_number = from_number

    def validate(self) -> None:
        if not self._account_sid:
            raise ValueError("account_sid is required for SMSNotifier")
        if not self._auth_token:
            raise ValueError("auth_token is required for SMSNotifier")
        if not self._to_number:
            raise ValueError("to_number is required for SMSNotifier")
        if not self._from_number:
            raise ValueError("from_number is required for SMSNotifier")

    def send(self, subject: str, message: str) -> None:
        client = Client(self._account_sid, self._auth_token)
        client.messages.create(
            to=self._to_number,
            from_=self._from_number,
            body=f"{subject}\n{message}",
        )
        logger.info("SMS sent to %s", self._to_number)
