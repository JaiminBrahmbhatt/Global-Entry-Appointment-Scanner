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
