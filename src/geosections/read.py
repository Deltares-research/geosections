import tomllib
import warnings
from pathlib import Path

import geopandas as gpd
import geost
import rioxarray as rio
import typer
import xarray as xr
from geost.validate.validate import ValidationWarning
from pandas.errors import SettingWithCopyWarning
from shapely import geometry as gmt

from geosections import base, utils

warnings.filterwarnings("ignore", category=ValidationWarning)
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)


def _geopandas_read(file: str | Path, **kwargs) -> gpd.GeoDataFrame:
    file = Path(file)
    if file.suffix in {".shp", ".gpkg"}:
        return gpd.read_file(file, **kwargs)
    elif file.suffix in {".parquet", ".geoparquet"}:
        return gpd.read_parquet(file, **kwargs)
    else:
        raise ValueError(f"File type {file.suffix} is not supported by geopandas.")


def read_config(file: str | Path) -> base.Config:
    """
    Read a TOML configuration file and return a Config object for `geosections` tools.

    Parameters
    ----------
    file : str | Path
        Pathlike object to the TOML configuration file.

    Returns
    -------
    :class:`~geosections.Config`
        Configuration object for `geosections` tools.

    """
    with open(file, "rb") as f:
        config = tomllib.load(f)

    try:
        config = base.Config(**config)
    except Exception as e:
        typer.secho(f"Invalid configuration:\n{e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    return config


def read_line(data: base.Line) -> gmt.LineString:
    """
    Retrieve the cross-section line from a shapefile or geoparquet and return it as a
    LineString object.

    Parameters
    ----------
    data : :class:`~geosections.base.Line`
        Data containing the cross-section line.

    Returns
    -------
    gmt.LineString
        Shapely LineString for the cross-section.

    Raises
    ------
    typer.Exit
        Raises an error when a `name_column` is not found in the input cross-section lines
        if attempting to select a specific line.

    """
    line = _geopandas_read(data.file)

    if line.crs is None or line.crs != 28992:
        line.set_crs(28992, allow_override=True, inplace=True)

    if data.name is not None:
        try:
            line = line[line[data.name_column] == data.name]["geometry"].iloc[0]
        except KeyError as e:
            typer.secho(
                f"'name_column' not found in input cross-section lines:\n{e}",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)
    else:
        line = line["geometry"].iloc[0]

    return line


def _select_line_data(
    data: geost.base.Collection,
    line: gmt.LineString,
    distance: int | float,
    additional_nrs: list[str] | None = None,
) -> geost.base.Collection:
    """
    Helper function to select data in a `geost.base.Collection` (or subclass) instance
    along a line within a specified distance and add optional additional data to the
    resulting `Collection` object.

    Parameters
    ----------
    data : geost.base.Collection
        `Collection` instance to select data from.
    line : gmt.LineString
        Shapely `LineString` instance to select data along.
    distance : int | float
        Maximum distance from the line to select data within.
    additional_nrs : list[str] | None, optional
        Optional additional data to select. The default is None.

    Returns
    -------
    geost.base.Collection
        `Collection` of the selected data along the line.

    """
    if additional_nrs is None:
        additional_nrs = []

    if data.horizontal_reference != 28992:
        data.change_horizontal_reference(28992)

    data_on_line = data.select_with_lines(line, buffer=distance)

    if additional_nrs:
        additional = data.get(additional_nrs)
        data_on_line = utils.concat(data_on_line, additional, ignore_index=True)

    return data_on_line


def read_boreholes(
    data: base.Data, line: gmt.LineString
) -> geost.base.BoreholeCollection:
    """
    Read the borehole data that will be plotted in the cross-section and determine the
    position (i.e. distance) of each borehole in the cross-section.

    Parameters
    ----------
    data : :class:`~geosections.base.Data`
        `Data` object for the borehole data to be plotted in the cross-section.
    line : gmt.LineString
        Shapely LineString for the cross-section.

    Returns
    -------
    `geost.base.BoreholeCollection`
        `BoreholeCollection` object containing the borehole data to be plotted in the
        cross-section with a new column "dist" containing the distance of each borehole
        from the start of the cross-section line.

    """
    boreholes = geost.read_borehole_table(data.file, horizontal_reference=data.crs)
    boreholes = _select_line_data(
        boreholes, line, data.max_distance_to_line, data.additional_nrs
    )
    boreholes.header["dist"] = utils.distance_on_line(boreholes, line)
    return boreholes


def read_cpts(data: base.Data, line: gmt.LineString) -> geost.base.BoreholeCollection:
    """
    Read the CPT data that will be plotted in the cross-section and determine the
    position (i.e. distance) of each CPT in the cross-section.

    Parameters
    ----------
    data : :class:`~geosections.base.Data`
        `Data` object for the CPT data to be plotted in the cross-section.
    line : gmt.LineString
        Shapely LineString for the cross-section.

    Returns
    -------
    `geost.base.BoreholeCollection`
        `BoreholeCollection` object containing the CPT data to be plotted in the
        cross-section with a new column "dist" containing the distance of each CPT from
        the start of the cross-section line.

    """
    cpts = geost.read_cpt_table(data.file, horizontal_reference=data.crs)
    cpts = _select_line_data(cpts, line, data.max_distance_to_line, data.additional_nrs)
    cpts = utils.cpts_to_borehole_collection(
        cpts,
        {
            "depth": ["min", "max"],
            "lith": "first",
        },
    )
    cpts.header["dist"] = utils.distance_on_line(cpts, line)
    cpts.add_header_column_to_data("surface")
    cpts.add_header_column_to_data("end")
    return cpts


def read_surface(data: base.Surface, line: gmt.LineString) -> xr.DataArray:
    """
    Read a raster surface and sample it along the cross-section line. The surface is
    reprojected to the same CRS as the cross-section line if necessary.

    Parameters
    ----------
    data : :class:`~geosections.base.Surface`
        `Surface` object containing the raster surface to be plotted in the cross-section.
    line : gmt.LineString
        Shapely LineString for the cross-section.

    Returns
    -------
    xr.DataArray
        `DataArray` object containing the sampled surface data along the cross-section
        line.

    """
    surface = rio.open_rasterio(data.file, masked=True).squeeze(drop=True)

    if surface.rio.crs is None:
        warning = (
            f"Surface {Path(data.file).stem} has no CRS, surface may not be shown correctly "
            "along the cross-section line."
        )
        typer.secho(warning, fg=typer.colors.YELLOW)
    elif surface.rio.crs != 28992:
        surface = surface.rio.reproject(28992)

    surface = geost.models.model_utils.sample_along_line(surface, line, dist=2.5)
    return surface


def read_curves(data: base.Curves, line: gmt.LineString) -> geost.base.CptCollection:
    """
    Read the CPT data for the curves that will be plotted in the cross-section and scale
    the cone resistance and friction ratio values to the distance of the cross-section line.

    Parameters
    ----------
    config : :class:`~geosections.base.Curves`
        `Curves` object containing the CPT data to plot the curves for in the cross-section.
    line : gmt.LineString
        Shapely LineString for the cross-section.

    Returns
    -------
    `geost.base.CptCollection`
        `CptCollection` object containing the CPT data for the curves to be plotted in the
        cross-section with the cone resistance and friction ratio data scaled to the
        cross-section line distance.
    """
    curves = geost.read_cpt_table(data.file, horizontal_reference=data.crs)

    if curves.horizontal_reference != 28992:
        curves.change_horizontal_reference(28992)

    curves = utils.get_cpt_curves_for_section(
        curves,
        data.nrs,
        line,
        dist_scale_factor=data.dist_scale_factor,
        qc_max=data.qc_max,
        fs_max=data.fs_max,
    )
    return curves
