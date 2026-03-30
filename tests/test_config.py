from pathlib import Path

import pytest

from global_entry_scanner.config import (
    load_config,
)


def write_toml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "config.toml"
    p.write_text(content)
    return p


def test_load_minimal_config(tmp_path: Path) -> None:
    p = write_toml(tmp_path, """
[scanner]
check_interval = 900
error_interval = 60
limit = 5

[locations]
ids = [5001, 5140]
""")
    cfg = load_config(p)
    assert cfg.locations.ids == [5001, 5140]
    assert cfg.scanner.check_interval == 900
    assert cfg.notifications.discord is None


def test_load_config_with_discord(tmp_path: Path) -> None:
    p = write_toml(tmp_path, """
[locations]
ids = [5001]

[notifications.discord]
webhook_url = "https://discord.com/api/webhooks/test"
""")
    cfg = load_config(p)
    assert cfg.notifications.discord is not None
    assert cfg.notifications.discord.webhook_url == "https://discord.com/api/webhooks/test"


def test_load_config_with_email(tmp_path: Path) -> None:
    p = write_toml(tmp_path, """
[locations]
ids = [5001]

[notifications.email]
from_email = "from@example.com"
to_email = "to@example.com"
password = "secret"
""")
    cfg = load_config(p)
    assert cfg.notifications.email is not None
    assert cfg.notifications.email.from_email == "from@example.com"


def test_load_config_raises_if_file_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="setup"):
        load_config(tmp_path / "nonexistent.toml")


def test_default_scanner_values(tmp_path: Path) -> None:
    p = write_toml(tmp_path, "[locations]\nids = [5001]")
    cfg = load_config(p)
    assert cfg.scanner.check_interval == 900
    assert cfg.scanner.error_interval == 60
    assert cfg.scanner.limit == 5


def test_load_config_email_with_smtp_fields(tmp_path: Path) -> None:
    p = write_toml(tmp_path, """
[locations]
ids = [5001]

[notifications.email]
from_email = "from@example.com"
to_email = "to@example.com"
password = "secret"
smtp_host = "smtp.office365.com"
smtp_port = 587
""")
    cfg = load_config(p)
    assert cfg.notifications.email is not None
    assert cfg.notifications.email.smtp_host == "smtp.office365.com"
    assert cfg.notifications.email.smtp_port == 587


def test_load_config_email_defaults_smtp(tmp_path: Path) -> None:
    """Existing configs without smtp_host/smtp_port get Gmail defaults."""
    p = write_toml(tmp_path, """
[locations]
ids = [5001]

[notifications.email]
from_email = "from@example.com"
to_email = "to@example.com"
password = "secret"
""")
    cfg = load_config(p)
    assert cfg.notifications.email is not None
    assert cfg.notifications.email.smtp_host == "smtp.gmail.com"
    assert cfg.notifications.email.smtp_port == 587


def test_save_config_email_writes_smtp_fields(tmp_path: Path) -> None:
    from global_entry_scanner.config import (
        Config,
        EmailConfig,
        LocationsConfig,
        NotificationConfig,
        ScannerConfig,
        save_config,
    )
    cfg = Config(
        locations=LocationsConfig(ids=[5001]),
        scanner=ScannerConfig(),
        notifications=NotificationConfig(
            email=EmailConfig(
                from_email="a@b.com",
                to_email="c@d.com",
                password="pw",
                smtp_host="smtp.mail.yahoo.com",
                smtp_port=587,
            )
        ),
    )
    p = tmp_path / "config.toml"
    save_config(cfg, p)
    text = p.read_text()
    assert 'smtp_host = "smtp.mail.yahoo.com"' in text
    assert "smtp_port = 587" in text
