import geost
import numpy as np
import pytest
import xarray as xr
from numpy.testing import assert_array_almost_equal, assert_array_equal
from shapely import geometry as gmt

from geosections import read


@pytest.mark.unittest
def test_read_config(configuration_toml):
    config = read.read_config(configuration_toml)
    assert config.line.file.name == "test_line.geoparquet"
    assert config.data.boreholes.file.name == "borehole_data.parquet"
    assert config.data.cpts.file.name == "cpt_data.parquet"
    assert config.data.curves.file.name == "cpt_data.parquet"
    assert config.surface[0].file.name == "test_surface.tif"


@pytest.mark.unittest
def test_read_line(config):
    line = read.read_line(config.line)
    assert isinstance(line, gmt.LineString)


@pytest.mark.unittest
def test_read_boreholes(config, test_line):
    config.data.boreholes.additional_nrs = ["D"]
    boreholes = read.read_boreholes(config.data.boreholes, test_line)
    assert isinstance(boreholes, geost.base.BoreholeCollection)
    assert boreholes.n_points == 4
    assert_array_equal(boreholes.header["nr"], ["A", "B", "C", "D"])
    assert_array_almost_equal(
        boreholes.header["dist"], [1.45521375, 0.24253563, 3.63803438, 1.940285]
    )


@pytest.mark.unittest
def test_read_cpts(config, test_line):
    cpts = read.read_cpts(config.data.cpts, test_line)
    assert isinstance(cpts, geost.base.BoreholeCollection)
    assert cpts.n_points == 2
    assert_array_equal(cpts.header["nr"], ["a", "b"])
    assert_array_almost_equal(cpts.header["dist"], [0.84887469, 1.69774938])


@pytest.mark.unittest
def test_read_curves(config, test_line):
    curves = read.read_curves(config.data.curves, test_line)
    assert isinstance(curves, geost.base.CptCollection)
    assert_array_equal(curves.header["nr"], ["a"])
    assert_array_almost_equal(curves.header["dist"], [0.84887469])
    assert np.all(
        np.abs(curves.data["qc"] - curves.data["dist"])
        <= config.data.curves.dist_scale_factor
    )
    assert np.all(
        np.abs(curves.data["fs"] - curves.data["dist"])
        <= config.data.curves.dist_scale_factor
    )


@pytest.mark.unittest
def test_read_surface(config, test_line):
    surface = read.read_surface(config.surface[0], test_line)
    assert isinstance(surface, xr.DataArray)
    assert surface.sizes == {"dist": 2}
    assert_array_almost_equal(surface, [0.6, 0.6])
