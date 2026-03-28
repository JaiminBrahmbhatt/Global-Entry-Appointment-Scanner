from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


class SlackNotifier:
    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url

    def validate(self) -> None:
        if not self._webhook_url:
            raise ValueError("webhook_url is required for SlackNotifier")

    def send(self, subject: str, message: str) -> None:
        payload = {"text": f"*{subject}*\n{message}"}
        response = requests.post(self._webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Slack notification sent")
