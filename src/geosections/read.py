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

    if boreholes.horizontal_reference != 28992:
        boreholes.change_horizontal_reference(28992)

    boreholes_line = boreholes.select_with_lines(line, buffer=data.max_distance_to_line)

    if data.additional_nrs:
        additional = boreholes.get(data.additional_nrs)
        boreholes_line = utils.concat(boreholes_line, additional, ignore_index=True)

    boreholes_line.header["dist"] = utils.distance_on_line(boreholes_line, line)
    return boreholes_line


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

    if cpts.horizontal_reference != 28992:
        cpts.change_horizontal_reference(28992)

    cpts_line = cpts.select_with_lines(line, buffer=data.max_distance_to_line)

    if data.additional_nrs:
        additional = cpts.get(data.additional_nrs)
        cpts_line = utils.concat(cpts_line, additional)

    cpts_line = utils.cpts_to_borehole_collection(
        cpts_line,
        {
            "depth": ["min", "max"],
            "lith": "first",
        },
    )
    cpts_line.header["dist"] = utils.distance_on_line(cpts_line, line)
    cpts_line.add_header_column_to_data("surface")
    cpts_line.add_header_column_to_data("end")
    return cpts_line


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


def read_curves(config: base.Config, line: gmt.LineString) -> geost.base.CptCollection:
    """
    Read the CPT data for the curves that will be plotted in the cross-section and scale
    the cone resistance and friction ratio values to the distance of the cross-section line.

    Parameters
    ----------
    config : :class:`~geosections.base.Config`
        `Config` object containing the configuration for the cross-section with the necessary
        data.
    line : gmt.LineString
        Shapely LineString for the cross-section.

    Returns
    -------
    `geost.base.CptCollection`
        `CptCollection` object containing the CPT data for the curves to be plotted in the
        cross-section with the cone resistance and friction ratio data scaled to the
        cross-section line distance.
    """
    curves = geost.read_cpt_table(
        config.data.cpts.file, horizontal_reference=config.data.cpts.crs
    )

    if curves.horizontal_reference != 28992:
        curves.change_horizontal_reference(28992)

    curves = utils.get_cpt_curves_for_section(
        curves,
        config.data.curves.nrs,
        line,
        dist_scale_factor=config.data.curves.dist_scale_factor,
    )
    return curves
