from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class PlotLabels(BaseModel):
    xlabel: str = Field("")
    ylabel: str = Field("")
    title: str = Field("")


class PlotSettings(BaseModel):
    width: int = Field(default=11)
    height: int = Field(default=7)
    inches: bool = Field(default=True)
    grid: bool = Field(default=True)
    dpi: int = Field(default=300)


class Surface(BaseModel):
    file: str
    style_kwds: dict[str, Any] = Field(default={})


class Data(BaseModel):
    file: str
    max_distance_to_line: int | float = Field(default=50)
    crs: int = Field(default=28992)


class Curves(BaseModel):
    nrs: list[str]
    dist_scale_factor: int | float = Field(default=80)


class PlotData(BaseModel):
    boreholes: Data = Field(default=None)
    cpts: Data = Field(default=None)
    curves: Curves = Field(default=None)


class Line(BaseModel):
    file: str | Path
    crs: int = Field(default=28992)
    name: Any = Field(default=None)


class Config(BaseModel):
    line: Line
    data: PlotData = Field(default=PlotData())
    surface: list[Surface] = Field(default=[])
    labels: PlotLabels = Field(default=PlotLabels())
    settings: PlotSettings = Field(default=PlotSettings())
    colors: dict[str, str] = Field({"default": "#000000"})


if __name__ == "__main__":
    import tomllib
    from pathlib import Path

    with open("test.toml", "rb") as f:
        data = tomllib.load(f)
    print(data)
