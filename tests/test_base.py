from pathlib import Path

import pytest
from pydantic import ValidationError

from geosections import base


class TestData:
    @pytest.mark.unittest
    def test_initialize(self, borehole_data):
        data = base.Data(**{"file": borehole_data})
        assert Path(data.file).name == "borehole_data.parquet"
        assert data.crs == 28992
        assert data.max_distance_to_line == 50
        assert not data.additional_nrs
        assert data.label

    @pytest.mark.unittest
    def test_initialize_with_non_default_input(self, borehole_data):
        data = base.Data(
            **{
                "file": borehole_data,
                "max_distance_to_line": 100,
                "crs": 4326,
                "additional_nrs": ["A", "B"],
                "label": False,
            }
        )
        assert Path(data.file).name == "borehole_data.parquet"
        assert data.crs == 4326
        assert data.max_distance_to_line == 100
        assert data.additional_nrs == ["A", "B"]
        assert not data.label

    def test_initialize_invalid_input(self, borehole_data):
        with pytest.raises(ValidationError):
            base.Data(
                **{
                    "file": borehole_data,
                    "max_distance_to_line": "invalid",
                    "crs": "4326",
                    "additional_nrs": ["A", "B"],
                    "label": False,
                }
            )
