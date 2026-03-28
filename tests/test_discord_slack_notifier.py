import json

import pytest
import responses as resp

from global_entry_scanner.notifications.discord import DiscordNotifier
from global_entry_scanner.notifications.slack import SlackNotifier

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/123/abc"
SLACK_WEBHOOK = "https://hooks.slack.com/services/T00/B00/xxx"


def test_discord_validate_raises_if_no_webhook() -> None:
    n = DiscordNotifier(webhook_url="")
    with pytest.raises(ValueError, match="webhook_url"):
        n.validate()


def test_discord_validate_passes_with_webhook() -> None:
    n = DiscordNotifier(webhook_url=DISCORD_WEBHOOK)
    n.validate()  # should not raise


@resp.activate
def test_discord_send_posts_to_webhook() -> None:
    resp.add(resp.POST, DISCORD_WEBHOOK, body=b"", status=204)
    n = DiscordNotifier(webhook_url=DISCORD_WEBHOOK)
    n.send("Test Subject", "Test body")
    assert len(resp.calls) == 1
    payload = json.loads(resp.calls[0].request.body)
    assert "Test Subject" in payload["content"]
    assert "Test body" in payload["content"]


def test_slack_validate_raises_if_no_webhook() -> None:
    n = SlackNotifier(webhook_url="")
    with pytest.raises(ValueError, match="webhook_url"):
        n.validate()


def test_slack_validate_passes_with_webhook() -> None:
    n = SlackNotifier(webhook_url=SLACK_WEBHOOK)
    n.validate()  # should not raise


@resp.activate
def test_slack_send_posts_to_webhook() -> None:
    resp.add(resp.POST, SLACK_WEBHOOK, json={"ok": True}, status=200)
    n = SlackNotifier(webhook_url=SLACK_WEBHOOK)
    n.send("Test Subject", "Test body")
    assert len(resp.calls) == 1
    payload = json.loads(resp.calls[0].request.body)
    assert "Test Subject" in payload["text"]
    assert "Test body" in payload["text"]
