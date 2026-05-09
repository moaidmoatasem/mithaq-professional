from typer.testing import CliRunner
from cherenkov.cli import app

runner = CliRunner()


def test_cli_help_succeeds():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "scan" in result.stdout
    assert "history" in result.stdout
    assert "list-scanners" in result.stdout


def test_cli_list_scanners_succeeds():
    result = runner.invoke(app, ["list-scanners"])
    assert result.exit_code == 0


def test_cli_history_succeeds():
    result = runner.invoke(app, ["history", "-n", "3"])
    assert result.exit_code == 0
