import pytest
from unittest.mock import MagicMock, patch
from global_entry_scanner.notifications.sms import SMSNotifier


def test_validate_raises_if_missing_account_sid() -> None:
    n = SMSNotifier(account_sid="", auth_token="token", to_number="+1234", from_number="+5678")
    with pytest.raises(ValueError, match="account_sid"):
        n.validate()


def test_validate_raises_if_missing_auth_token() -> None:
    n = SMSNotifier(account_sid="sid", auth_token="", to_number="+1234", from_number="+5678")
    with pytest.raises(ValueError, match="auth_token"):
        n.validate()


def test_validate_raises_if_missing_to_number() -> None:
    n = SMSNotifier(account_sid="sid", auth_token="token", to_number="", from_number="+5678")
    with pytest.raises(ValueError, match="to_number"):
        n.validate()


def test_validate_raises_if_missing_from_number() -> None:
    n = SMSNotifier(account_sid="sid", auth_token="token", to_number="+1234", from_number="")
    with pytest.raises(ValueError, match="from_number"):
        n.validate()


def test_validate_passes_with_all_fields() -> None:
    n = SMSNotifier(account_sid="sid", auth_token="token", to_number="+1234", from_number="+5678")
    n.validate()  # should not raise


def test_send_calls_twilio_client() -> None:
    n = SMSNotifier(account_sid="sid", auth_token="token", to_number="+1234", from_number="+5678")
    with patch("global_entry_scanner.notifications.sms.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        n.send("Subject", "Body")
        mock_client_cls.assert_called_once_with("sid", "token")
        mock_client.messages.create.assert_called_once_with(
            to="+1234", from_="+5678", body="Subject\nBody"
        )
