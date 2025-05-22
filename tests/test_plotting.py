import pytest

from geosections import plotting


@pytest.mark.unittest
def test_plot_cross_section(configuration_toml, tmp_path):
    outfile = tmp_path / "test.png"
    plotting.plot_cross_section(configuration_toml, outfile, True)
    assert outfile.exists()

