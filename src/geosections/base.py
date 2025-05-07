from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class PlotLabels(BaseModel):
    xlabel: str = Field("")
    ylabel: str = Field("")
    title: str = Field("")


class PlotSettings(BaseModel):
    column_with: int | float = Field(default=20)
    fig_width: int = Field(default=11)
    fig_height: int = Field(default=7)
    inches: bool = Field(default=True)
    grid: bool = Field(default=True)
    dpi: int = Field(default=300)
    tight_layout: bool = Field(default=True)
    ymin: int | float = Field(default=None)
    ymax: int | float = Field(default=None)


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
    name_column: str = Field(default="name")


class Config(BaseModel):
    line: Line
    data: PlotData = Field(default=PlotData())
    surface: list[Surface] = Field(default=[])
    labels: PlotLabels = Field(default=PlotLabels())
    settings: PlotSettings = Field(default=PlotSettings())
    colors: dict[str, str] = Field({"default": "#000000"})
