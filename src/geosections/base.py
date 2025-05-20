from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class PlotLabels(BaseModel):
    """
    General labels to apply to the cross-section.

    Parameters
    ----------
    xlabel : str
        X-axis label for the cross-section.
    ylabel : str
        Y-axis label for the cross-section.
    title : str
        Main title for the cross-section.
    """

    xlabel: str = Field(default="")
    ylabel: str = Field(default="")
    title: str = Field(default="")


class PlotSettings(BaseModel):
    """
    General settings for the cross-section plot.

    Parameters
    ----------
    column_with : int | float
        Width of the borehole columns in the cross-section in meters.
    fig_width : int | float
        Width of the figure in inches or centimeters.
    fig_height : int | float
        Height of the figure in inches or centimeters.
    inches : bool
        If True, fig_width and fig_height are given in inches. If False, they are in given
        in centimeters.
    grid : bool
        If True, a grid is drawn in the background of the cross-section.
    dpi : int
        Dots per inch for the figure if it is saved to a file.
    tight_layout : bool
        If True, uses Matplotlib's `plt.subplots(tight_layout=True)`.
    ymin : int | float
        Minimum depth of the cross-section.
    ymax : int | float
        Maximum depth of the cross-section.
    xmin : int | float
        Minimum distance of the cross-section.
    xmax : int | float
        Maximum distance of the cross-section.
    """

    column_with: int | float = Field(default=20)
    fig_width: int | float = Field(default=11)
    fig_height: int | float = Field(default=7)
    inches: bool = Field(default=True)
    grid: bool = Field(default=True)
    dpi: int = Field(default=300)
    tight_layout: bool = Field(default=True)
    ymin: int | float = Field(default=None)
    ymax: int | float = Field(default=None)
    xmin: int | float = Field(default=None)
    xmax: int | float = Field(default=None)


class Surface(BaseModel):
    """
    Base object for plotting a surface from a raster in the cross-section.

    Parameters
    ----------
    file : str
        Filepath-like string to the raster file that can be opened by `rioxarray.open_rasterio`.
    style_kwds : dict[str, Any]
        Keyword arguments for the style of the surface line which are passed to
        `matplotlib.pyplot.plot`. For example, `{"color": "red", "linestyle": "--"}`.
    """

    file: str
    style_kwds: dict[str, Any] = Field(default={})


class Data(BaseModel):
    """
    Base object for plotting borehole or CPT data in the cross-section.

    Parameters
    ----------
    file : str
        Filepath-like string (e.g. my-file.parquet, my-file.csv) to the borehole or CPT
        data file.
    max_distance_to_line : int | float
        Maximum distance to the cross-section line in meters. This is used to select the
        boreholes or CPTs that are within this distance to the line.
    crs : int
        Coordinate reference system of the borehole or CPT data. Default is 28992 (RD New).
    additional_nrs : list[str]
        List of additional borehole or CPT numbers to plot in the cross-section. For example,
        to plot boreholes or CPTs that are outside the maximum distance to the line.
    """

    file: str
    max_distance_to_line: int | float = Field(default=50)
    crs: int = Field(default=28992)
    additional_nrs: list[str] = Field(default=[])
    label: bool = Field(default=True)


class Curves(BaseModel):
    """
    Base object for plotting cone resistance and friction ratio curves from CPT data in
    the cross-section.

    Parameters
    ----------
    nrs : list[str]
        List of CPT numbers to plot the CPT curves for in the cross-section.
    dist_scale_factor : int | float
        Scale factor of the distance in meters to determine the width of the curves from in
        the cross-section. All values in the CPT data are scaled between 0 (min) and 1 (max)
        meters using Scikit-learn's `MinMaxScaler` (see relevant documentation). The width
        of the each curve in the cross-section is calculated by:
        `x scaled * dist_scale_factor`.
    """

    nrs: list[str]
    dist_scale_factor: int | float = Field(default=80)
    label: bool = Field(default=False)


class PlotData(BaseModel):
    """
    Container for the borehole, CPT and curve data to be plotted in the cross-section.

    Parameters
    ----------
    boreholes : :class:`~Data`
        `Data` object for the borehole data to be plotted in the cross-section.
    cpts : :class:`~Data`
        `Data` object for the CPT data to be plotted in the cross-section.
    curves : :class:`~Curves`
        `Curves` object for the CPT curves to be plotted in the cross-section.
    """

    boreholes: Data = Field(default=None)
    cpts: Data = Field(default=None)
    curves: Curves = Field(default=None)


class Line(BaseModel):
    """
    Base object containing the line for the cross-section.

    Parameters
    ----------
    file : str
        Filepath-like string to the line file that can be opened by `geopandas.read_file`
        or `geopandas.read_parquet`.
    crs : int
        Coordinate reference system of the line. Default is 28992 (RD New).
    name : Any
        Attribute name of the line to plot. If None, the first line in the file is used.
    name_column : str
        Name of the attribute column to select the `name` parameter from. The default is
        "name". If the column is not found, the first line in the file is used.
    """

    file: str | Path
    crs: int = Field(default=28992)
    name: Any = Field(default=None)
    name_column: str = Field(default="name")


class Config(BaseModel):
    """
    Configuration object for the cross-section containing the line, plot data and associated
    settings.

    Parameters
    ----------
    line : :class:`~Line`
        `Line` object containing the line for the cross-section.
    data : :class:`~PlotData`
        `PlotData` object containing the borehole, CPT and curve data for the cross-section.
    surface : list[:class:`~Surface`]
        List of `Surface` objects containing the surfaces to be plotted in the cross-section.
    labels : :class:`~PlotLabels`
        `PlotLabels` object containing the labels for the cross-section.
    settings : :class:`~PlotSettings`
        `PlotSettings` object containing the settings for the cross-section.
    colors : dict[str, str]
        Dictionary of colors to use for the cross-section specifying a color for each each
        lithology to distinguish between. For example: {"clay": "g", "sand": "y"}.
    """

    line: Line
    data: PlotData = Field(default=PlotData())
    surface: list[Surface] = Field(default=[])
    labels: PlotLabels = Field(default=PlotLabels())
    settings: PlotSettings = Field(default=PlotSettings())
    colors: dict[str, str] = Field({"default": "#000000"})
