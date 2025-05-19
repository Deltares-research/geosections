import pytest
from typer.testing import CliRunner

from geosections.cli import app

runner = CliRunner()


def test_help():
    command_name = "--help"
    args = [command_name]

    result = runner.invoke(app, args)
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "Options" in result.output
    assert "Commands" in result.output


# Test to debug the app locally
@pytest.mark.skip(reason="For local testing only")
def test_debug_app():
    command_name = "plot"
    args = [
        command_name,
        r"n:\Projects\11209500\11209639\C. Report - advise\Geological site evaluation Eemshaven\Figures\geosections_settings\gs_e3_nwzo.toml",
        "--save",
        r"n:\Projects\11209500\11209639\C. Report - advise\Geological site evaluation Eemshaven\Figures\gs_e3_nwzo.png",
    ]

    result = runner.invoke(app, args)
    assert result.exit_code == 0
