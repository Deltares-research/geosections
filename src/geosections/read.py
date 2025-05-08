import tomllib
from pathlib import Path

import geopandas as gpd
import geost
import rioxarray as rio
import typer
import xarray as xr
from shapely import geometry as gmt

from geosections import base, utils


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
    boreholes = geost.read_borehole_table(data.file, horizontal_reference=data.crs)

    if boreholes.horizontal_reference != 28992:
        boreholes.change_horizontal_reference(28992)

    boreholes = boreholes.select_with_lines(line, buffer=data.max_distance_to_line)
    boreholes.header["dist"] = utils.distance_on_line(boreholes, line)
    return boreholes


def read_cpts(data: base.Data, line: gmt.LineString) -> geost.base.BoreholeCollection:
    cpts = geost.read_cpt_table(data.file, horizontal_reference=data.crs)

    if cpts.horizontal_reference != 28992:
        cpts.change_horizontal_reference(28992)

    cpts = utils.cpts_to_borehole_collection(
        cpts.select_with_lines(line, buffer=30),
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
