import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import rioxarray as rio
import toml
import xarray as xr
from shapely import geometry as gmt

from geosections.read import read_config


def borehole_a():
    nlayers = 5
    top = [0, 0.8, 1.5, 2.5, 3.7]
    bottom = top[1:] + [4.2]
    mv = 0.2
    end = mv - bottom[-1]
    return pd.DataFrame(
        {
            "nr": np.full(nlayers, "A"),
            "x": np.full(nlayers, 2),
            "y": np.full(nlayers, 3),
            "surface": np.full(nlayers, mv),
            "end": np.full(nlayers, end),
            "top": top,
            "bottom": bottom,
            "lith": ["K", "K", "Z", "Z", "K"],
        }
    )


def borehole_b():
    nlayers = 5
    top = [0, 0.6, 1.2, 2.5, 3.1]
    bottom = top[1:] + [3.9]
    mv = 0.3
    end = mv - bottom[-1]
    return pd.DataFrame(
        {
            "nr": np.full(nlayers, "B"),
            "x": np.full(nlayers, 1),
            "y": np.full(nlayers, 4),
            "surface": np.full(nlayers, mv),
            "end": np.full(nlayers, end),
            "top": top,
            "bottom": bottom,
            "lith": ["K", "K", "V", "V", "K"],
        }
    )


def borehole_c():
    nlayers = 5
    top = [0, 1.4, 1.8, 2.9, 3.8]
    bottom = top[1:] + [5.5]
    mv = 0.25
    end = mv - bottom[-1]
    return pd.DataFrame(
        {
            "nr": np.full(nlayers, "C"),
            "x": np.full(nlayers, 4),
            "y": np.full(nlayers, 2),
            "surface": np.full(nlayers, mv),
            "end": np.full(nlayers, end),
            "top": top,
            "bottom": bottom,
            "lith": ["K", "K", "K", "Z", "Z"],
        }
    )


def borehole_d():
    nlayers = 5
    top = [0, 0.5, 1.2, 1.8, 2.5]
    bottom = top[1:] + [3.0]
    mv = 0.1
    end = mv - bottom[-1]
    return pd.DataFrame(
        {
            "nr": np.full(nlayers, "D"),
            "x": np.full(nlayers, 3),
            "y": np.full(nlayers, 5),
            "surface": np.full(nlayers, mv),
            "end": np.full(nlayers, end),
            "top": top,
            "bottom": bottom,
            "lith": ["K", "V", "K", "V", "Z"],
        }
    )


def borehole_e():
    nlayers = 5
    top = [0, 0.5, 1.2, 1.8, 2.5]
    bottom = top[1:] + [3.0]
    mv = -0.1
    end = mv - bottom[-1]
    return pd.DataFrame(
        {
            "nr": np.full(nlayers, "E"),
            "x": np.full(nlayers, 1),
            "y": np.full(nlayers, 1),
            "surface": np.full(nlayers, mv),
            "end": np.full(nlayers, end),
            "top": top,
            "bottom": bottom,
            "lith": ["Z", "Z", "Z", "Z", "Z"],
        }
    )


def cpt_a():
    """
    Helper function for a synthetic CPT containing qs, fs and u2 "measurements".

    """
    depth = np.arange(10)
    surface = 0.7
    end = surface - depth.max()
    qc = [0.227, 0.279, 0.327, 0.354, 0.357, 0.354, 0.363, 0.447, 0.761, 1.481]
    fs = [0.010, 0.014, 0.019, 0.021, 0.022, 0.023, 0.026, 0.023, 0.022, 0.021]
    lith = ["Kh", "V", "V", "V", "V", "V", "V", "V", "K", "Kz"]
    return pd.DataFrame(
        {
            "nr": np.repeat("a", 10),
            "x": np.repeat(1, 10),
            "y": np.repeat(1.5, 10),
            "surface": np.repeat(surface, 10),
            "end": np.repeat(end, 10),
            "depth": depth,
            "cone_resistance": qc,
            "friction_ratio": fs,
            "lith": lith,
        }
    )


def cpt_b():
    """
    Helper function for a synthetic CPT containing qs, fs and u2 "measurements".

    """
    depth = np.arange(10)
    surface = 0.8
    end = surface - depth.max()
    qc = [8.721, 12.733, 17.324, 17.036, 16.352, 15.781, 15.365, 15.509, 15.884, 15.982]
    fs = [0.061, 0.058, 0.055, 0.054, 0.052, 0.051, 0.052, 0.051, 0.051, 0.050]
    lith = ["Z", "Z", "Z", "Z", "Z", "Z", "Z", "Z", "Z", "Z"]
    return pd.DataFrame(
        {
            "nr": np.repeat("b", 10),
            "x": np.repeat(2, 10),
            "y": np.repeat(2, 10),
            "surface": np.repeat(surface, 10),
            "end": np.repeat(end, 10),
            "depth": depth,
            "cone_resistance": qc,
            "friction_ratio": fs,
            "lith": lith,
        }
    )


@pytest.fixture
def borehole_data(tmp_path):
    outfile = tmp_path / "borehole_data.parquet"
    df = pd.concat(
        [
            borehole_a(),
            borehole_b(),
            borehole_c(),
            borehole_d(),
            borehole_e(),
        ],
        ignore_index=True,
    )
    df.to_parquet(outfile, index=False)
    return str(outfile)


@pytest.fixture
def cpt_data(tmp_path):
    outfile = tmp_path / "cpt_data.parquet"
    df = pd.concat(
        [
            cpt_a(),
            cpt_b(),
        ],
        ignore_index=True,
    )
    df.to_parquet(outfile, index=False)
    return str(outfile)


@pytest.fixture
def test_line():
    return gmt.LineString([[0.5, 3.0], [4.5, 2.0]])


@pytest.fixture
def test_line_file(tmp_path, test_line):
    outfile = tmp_path / "test_line.geoparquet"
    gdf = gpd.GeoDataFrame(
        {"name": ["test_line"]},
        geometry=[test_line],
        crs=28992,
    )
    gdf.to_parquet(outfile)
    return str(outfile)


@pytest.fixture
def test_surface(tmp_path):
    outfile = tmp_path / "test_surface.tif"
    da = xr.DataArray(
        [
            [0.55, 0.55, 0.55, 0.55, 0.55],
            [0.6, 0.6, 0.6, 0.6, 0.6],
            [0.6, 0.6, 0.6, 0.6, 0.6],
            [0.55, 0.55, 0.55, 0.55, 0.55],
            [0.5, 0.5, 0.5, 0.5, 0.5],
        ],
        coords={"y": [4.5, 3.5, 2.5, 1.5, 0.5], "x": [0.5, 1.5, 2.5, 3.5, 4.5]},
        dims=("y", "x"),
    )
    da.rio.write_crs(28992, inplace=True)
    da.rio.to_raster(outfile)
    return str(outfile)


@pytest.fixture
def configuration_toml(tmp_path, test_line_file, borehole_data, cpt_data, test_surface):
    config = {
        "settings": {"column_width": 0.15},
        "line": {"file": test_line_file},
        "data": {
            "boreholes": {"file": borehole_data, "max_distance_to_line": 1.5},
            "cpts": {"file": cpt_data, "max_distance_to_line": 1.5},
            "curves": {"file": cpt_data, "nrs": ["a"], "dist_scale_factor": 0.2},
        },
        "surface": [{"file": test_surface}],
        "labels": {"xlabel": "x", "ylabel": "y"},
        "colors": {"K": "#175118", "V": "#714425", "Z": "#EACE1E"},
    }
    outfile = tmp_path / "test.toml"
    with open(outfile, "w") as f:
        toml.dump(config, f)
    return outfile


@pytest.fixture
def config(configuration_toml):
    return read_config(configuration_toml)
