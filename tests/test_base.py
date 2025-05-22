from pathlib import Path

import pytest
from pydantic import ValidationError

from geosections import base


@pytest.fixture
def non_default_borehole_input():
    return {
        "file": "test_borehole_data.parquet",
        "max_distance_to_line": 100,
        "crs": 4326,
        "additional_nrs": ["A", "B"],
        "label": True,
    }


@pytest.fixture
def non_default_cpt_input():
    return {
        "file": "test_cpt_data.parquet",
        "max_distance_to_line": 100,
        "crs": 4326,
        "additional_nrs": ["A", "B"],
        "label": True,
    }


@pytest.fixture
def non_default_curves_input():
    return {
        "file": "test_cpt_data.parquet",
        "crs": 4326,
        "dist_scale_factor": 100,
        "nrs": ["A", "B"],
        "label": True,
        "qc_max": 100,
        "fs_max": 100,
    }


@pytest.fixture
def non_default_line_input():
    return {
        "file": "test_line.geoparquet",
        "crs": 4326,
        "name": "test_line",
        "name_column": "test_name",
    }


@pytest.fixture
def non_default_surface_input():
    return {
        "file": "test_surface.tif",
        "style_kwds": {"color": "red", "alpha": 0.5},
    }


@pytest.fixture
def non_default_settings_input():
    return {
        "column_width": 30,
        "fig_width": 15,
        "fig_height": 10,
        "inches": False,
        "grid": False,
        "dpi": 600,
        "tight_layout": False,
        "ymin": 0,
        "ymax": 100,
        "xmin": 0,
        "xmax": 200,
    }


class TestData:
    @pytest.mark.unittest
    def test_initialize(self):
        data = base.Data(**{"file": "test_borehole_data.parquet"})
        assert isinstance(data.file, Path)
        assert data.file.name == "test_borehole_data.parquet"
        assert data.crs == 28992
        assert data.max_distance_to_line == 50
        assert not data.additional_nrs
        assert not data.label

    @pytest.mark.unittest
    def test_initialize_with_non_default_input(self, non_default_borehole_input):
        data = base.Data(**non_default_borehole_input)
        assert data.file.name == "test_borehole_data.parquet"
        assert data.crs == 4326
        assert data.max_distance_to_line == 100
        assert data.additional_nrs == ["A", "B"]
        assert data.label

    @pytest.mark.unittest
    def test_initialize_invalid_input(self):
        with pytest.raises(ValidationError) as e:
            base.Data(
                **{
                    "file": "test_borehole_data.parquet",
                    "max_distance_to_line": "invalid",
                    "crs": "invalid",
                    "additional_nrs": "invalid",
                    "label": "invalid",
                }
            )
            assert "max_distance_to_line" in str(e.value)
            assert "crs" in str(e.value)
            assert "additional_nrs" in str(e.value)


class TestCurves:
    @pytest.mark.unittest
    def test_initialize(self):
        data = base.Curves(**{"file": "test_cpt_data.parquet", "nrs": ["A", "B"]})
        assert isinstance(data.file, Path)
        assert data.file.name == "test_cpt_data.parquet"
        assert data.crs == 28992
        assert data.dist_scale_factor == 80
        assert data.nrs == ["A", "B"]
        assert not data.label
        assert data.qc_max is None
        assert data.fs_max is None

    @pytest.mark.unittest
    def test_initialize_with_non_default_input(self, non_default_curves_input):
        data = base.Curves(**non_default_curves_input)
        assert data.file.name == "test_cpt_data.parquet"
        assert data.crs == 4326
        assert data.dist_scale_factor == 100
        assert data.nrs == ["A", "B"]
        assert data.label
        assert data.qc_max == 100
        assert data.fs_max == 100

    @pytest.mark.unittest
    def test_initialize_invalid_input(self):
        with pytest.raises(ValidationError) as e:
            base.Curves(
                **{
                    "file": "test_cpt_data.parquet",
                    "crs": "invalid",
                    "dist_scale_factor": "invalid",
                    "nrs": "invalid",
                    "label": "invalid",
                    "qc_max": "invalid",
                    "fs_max": "invalid",
                }
            )
            assert "crs" in str(e.value)
            assert "dist_scale_factor" in str(e.value)
            assert "nrs" in str(e.value)
            assert "label" in str(e.value)
            assert "qc_max" in str(e.value)
            assert "fs_max" in str(e.value)


class TestLine:
    @pytest.mark.unittest
    def test_initialize(self):
        data = base.Line(**{"file": "test_line.geoparquet"})
        assert isinstance(data.file, Path)
        assert data.file.name == "test_line.geoparquet"
        assert data.crs == 28992
        assert data.name is None
        assert data.name_column == "name"

    @pytest.mark.unittest
    def test_initialize_with_non_default_input(self, non_default_line_input):
        data = base.Line(**non_default_line_input)
        assert data.file.name == "test_line.geoparquet"
        assert data.crs == 4326
        assert data.name == "test_line"
        assert data.name_column == "test_name"

    @pytest.mark.unittest
    def test_initialize_invalid_input(self):
        with pytest.raises(ValidationError) as e:
            base.Line(
                **{
                    "file": "test_line.geoparquet",
                    "crs": "invalid",
                }
            )
            assert "crs" in str(e.value)


class TestSurface:
    @pytest.mark.unittest
    def test_initialize(self):
        data = base.Surface(**{"file": "test_surface.tif"})
        assert isinstance(data.file, Path)
        assert data.file.name == "test_surface.tif"
        assert not data.style_kwds

    @pytest.mark.unittest
    def test_initialize_with_non_default_input(self, non_default_surface_input):
        data = base.Surface(**non_default_surface_input)
        assert data.file.name == "test_surface.tif"
        assert data.style_kwds == {"color": "red", "alpha": 0.5}

    @pytest.mark.unittest
    def test_initialize_invalid_input(self):
        with pytest.raises(ValidationError) as e:
            base.Surface(
                **{
                    "file": "test_surface.tif",
                    "style_kwds": "invalid",
                }
            )
            assert "style_kwds" in str(e.value)


class TestPlotSettings:
    @pytest.mark.unittest
    def test_initialize(self):
        settings = base.PlotSettings()
        assert settings.column_width == 20
        assert settings.fig_width == 11
        assert settings.fig_height == 7
        assert settings.inches
        assert settings.grid
        assert settings.dpi == 300
        assert settings.tight_layout
        assert settings.ymin is None
        assert settings.ymax is None
        assert settings.xmin is None
        assert settings.xmax is None

    @pytest.mark.unittest
    def test_initialize_with_non_default_input(self, non_default_settings_input):
        settings = base.PlotSettings(**non_default_settings_input)
        assert settings.column_width == 30
        assert settings.fig_width == 15
        assert settings.fig_height == 10
        assert not settings.inches
        assert not settings.grid
        assert settings.dpi == 600
        assert not settings.tight_layout
        assert settings.ymin == 0
        assert settings.ymax == 100
        assert settings.xmin == 0
        assert settings.xmax == 200

    @pytest.mark.unittest
    def test_initialize_invalid_input(self):
        with pytest.raises(ValidationError) as e:
            base.PlotSettings(
                **{
                    "column_width": "invalid",
                    "fig_width": "invalid",
                    "fig_height": "invalid",
                    "inches": "invalid",
                    "grid": "invalid",
                    "dpi": "invalid",
                    "tight_layout": "invalid",
                    "ymin": "invalid",
                    "ymax": "invalid",
                    "xmin": "invalid",
                    "xmax": "invalid",
                }
            )
            assert "column_width" in str(e.value)
            assert "fig_width" in str(e.value)
            assert "fig_height" in str(e.value)
            assert "inches" in str(e.value)
            assert "grid" in str(e.value)
            assert "dpi" in str(e.value)
            assert "tight_layout" in str(e.value)
            assert "ymin" in str(e.value)
            assert "ymax" in str(e.value)
            assert "xmin" in str(e.value)
            assert "xmax" in str(e.value)


class TestConfig:
    @pytest.fixture
    def all_input(
        self,
        non_default_borehole_input,
        non_default_cpt_input,
        non_default_curves_input,
        non_default_line_input,
        non_default_surface_input,
        non_default_settings_input,
    ):
        return {
            "line": non_default_line_input,
            "data": {
                "boreholes": non_default_borehole_input,
                "cpts": non_default_cpt_input,
                "curves": non_default_curves_input,
            },
            "surface": [non_default_surface_input],
            "settings": non_default_settings_input,
            "labels": {
                "xlabel": "X-axis label",
                "ylabel": "Y-axis label",
                "title": "Main title",
            },
            "colors": {"red": "#9F3131", "blue": "#313F9F"},
        }

    @pytest.mark.unittest
    def test_initialize_only_line(self, test_line_file):
        config = base.Config(**{"line": {"file": test_line_file}})
        assert isinstance(config.line, base.Line)
        assert isinstance(config.data, base.PlotData)
        assert config.data.boreholes is None
        assert config.data.cpts is None
        assert config.data.curves is None
        assert not config.surface
        assert isinstance(config.settings, base.PlotSettings)
        assert isinstance(config.labels, base.PlotLabels)
        assert isinstance(config.colors, dict)
        assert config.colors == {"default": "#000000"}

    @pytest.mark.unittest
    def test_initialize_all_input(self, all_input):
        config = base.Config(**all_input)
        assert config.line.file.name == "test_line.geoparquet"
        assert config.line.crs == 4326
        assert config.line.name == "test_line"
        assert config.line.name_column == "test_name"
        assert config.data.boreholes.file.name == "test_borehole_data.parquet"
        assert config.data.boreholes.max_distance_to_line == 100
        assert config.data.boreholes.crs == 4326
        assert config.data.boreholes.additional_nrs == ["A", "B"]
        assert config.data.boreholes.label
        assert config.data.cpts.file.name == "test_cpt_data.parquet"
        assert config.data.cpts.max_distance_to_line == 100
        assert config.data.cpts.crs == 4326
        assert config.data.cpts.additional_nrs == ["A", "B"]
        assert config.data.cpts.label
        assert config.data.curves.file.name == "test_cpt_data.parquet"
        assert config.data.curves.crs == 4326
        assert config.data.curves.dist_scale_factor == 100
        assert config.data.curves.nrs == ["A", "B"]
        assert config.data.curves.label
        assert config.data.curves.qc_max == 100
        assert config.data.curves.fs_max == 100
        assert config.surface[0].file.name == "test_surface.tif"
        assert config.surface[0].style_kwds == {"color": "red", "alpha": 0.5}
        assert config.settings.column_width == 30
        assert config.settings.fig_width == 15
        assert config.settings.fig_height == 10
        assert not config.settings.inches
        assert not config.settings.grid
        assert config.settings.dpi == 600
        assert not config.settings.tight_layout
        assert config.settings.ymin == 0
        assert config.settings.ymax == 100
        assert config.settings.xmin == 0
        assert config.settings.xmax == 200
        assert config.labels.xlabel == "X-axis label"
        assert config.labels.ylabel == "Y-axis label"
        assert config.labels.title == "Main title"
        assert config.colors == {"red": "#9F3131", "blue": "#313F9F"}
