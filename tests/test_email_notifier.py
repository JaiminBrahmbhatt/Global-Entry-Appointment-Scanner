from unittest.mock import MagicMock, patch

import pytest

from global_entry_scanner.notifications.email import EmailNotifier


def test_validate_raises_if_missing_from() -> None:
    n = EmailNotifier(from_email="", to_email="to@example.com", password="pass")
    with pytest.raises(ValueError, match="from_email"):
        n.validate()


def test_validate_raises_if_missing_to() -> None:
    n = EmailNotifier(from_email="from@example.com", to_email="", password="pass")
    with pytest.raises(ValueError, match="to_email"):
        n.validate()


def test_validate_raises_if_missing_password() -> None:
    n = EmailNotifier(from_email="from@example.com", to_email="to@example.com", password="")
    with pytest.raises(ValueError, match="password"):
        n.validate()


def test_validate_passes_with_all_fields() -> None:
    n = EmailNotifier(from_email="from@example.com", to_email="to@example.com", password="pass")
    n.validate()  # should not raise


def test_send_connects_and_sends() -> None:
    n = EmailNotifier(from_email="from@example.com", to_email="to@example.com", password="pass")
    with patch("global_entry_scanner.notifications.email.smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_smtp_cls.return_value = mock_server
        n.send("Test Subject", "Test message body")
        mock_smtp_cls.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("from@example.com", "pass")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
