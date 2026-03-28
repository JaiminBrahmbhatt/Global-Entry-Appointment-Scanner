import os
from pathlib import Path

import responses as resp
from click.testing import CliRunner

from global_entry_scanner.cli import cli
from global_entry_scanner.scanner import LOCATIONS_API_URL
from tests.conftest import MOCK_LOCATIONS

runner = CliRunner()


@resp.activate
def test_locations_command_lists_cities() -> None:
    resp.add(resp.GET, LOCATIONS_API_URL, json=MOCK_LOCATIONS)
    result = runner.invoke(cli, ["locations"])
    assert result.exit_code == 0
    assert "Mission" in result.output
    assert "Chicago" in result.output


def test_scan_command_errors_without_config(tmp_path: Path) -> None:
    result = runner.invoke(
        cli, ["scan"], env={"GES_CONFIG_PATH": str(tmp_path / "nonexistent.toml")}
    )
    assert result.exit_code != 0
    assert "setup" in result.output.lower()
