import geost
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

type BoreholeCollection = geost.base.BoreholeCollection
type CptCollection = geost.base.CptCollection
type Collection = geost.base.Collection


def cpts_to_borehole_collection(
    cpts: CptCollection, aggfuncs: dict
) -> BoreholeCollection:
    _, lith_nrs = np.unique(cpts.data["lith"], return_inverse=True)
    cpts.data["lith_nr"] = lith_nrs

    cpts_top_bot = cpts_as_top_bottom(cpts, aggfuncs, "lith_nr")
    cpts_top_bot.rename(
        columns={"depth_min": "top", "depth_max": "bottom"}, inplace=True
    )
    layered = geost.base.LayeredData(cpts_top_bot, has_inclined=False)
    result = geost.base.BoreholeCollection(cpts.header, layered)
    return result


def cpts_as_top_bottom(
    cpts: CptCollection, aggfuncs: dict, layer_col: str
) -> pd.DataFrame:
    data = cpts.data.df.copy()
    data["layer"] = create_layer_numbers(cpts, layer_col)

    cpts_as_top_bot = pd.pivot_table(
        data,
        index=["nr", "layer"],
        aggfunc=aggfuncs,
        sort=False,
    )

    cpts_as_top_bot.columns = _get_columns(aggfuncs)
    cpts_as_top_bot.reset_index(inplace=True)
    return cpts_as_top_bot


def _get_columns(aggfuncs: dict):
    for key, value in aggfuncs.items():
        if isinstance(value, str):
            yield key
        else:
            for v in value:
                yield f"{key}_{v}"


def create_layer_numbers(collection: Collection, layer_col: str) -> pd.Series:
    return (
        collection.data.df.groupby("nr")
        .apply(
            lambda x: label_consecutive_elements(x[layer_col].values),
            include_groups=False,
        )
        .explode()
        .values
    )


def label_consecutive_elements(array: np.ndarray) -> np.ndarray:
    """
    Label consecutive elements in an array.

    Parameters:
    -----------
    array : np.ndarray
        The array to label.

    Returns:
    --------
    np.ndarray
        The labeled array.

    """
    diff = np.diff(array, prepend=array[0])
    return np.cumsum(diff != 0)


def distance_on_line(collection, line):
    return line.project(collection.header["geometry"])


def get_cpt_curves_for_section(cpt_data, nrs, line, dist_scale_factor=80):
    cpt_curves = cpt_data.get(nrs)
    cpt_curves.header["dist"] = line.project(cpt_curves.header.gdf["geometry"])

    scaler = MinMaxScaler()
    cpt_curves.data["qc"] = (
        scaler.fit_transform(cpt_curves.data["cone_resistance"].values.reshape(-1, 1))
        * dist_scale_factor
    )
    cpt_curves.data["fs"] = (
        scaler.fit_transform(cpt_curves.data["friction_ratio"].values.reshape(-1, 1))
        * dist_scale_factor
    )
    cpt_curves.data["depth"] = cpt_curves.data["surface"] - cpt_curves.data["depth"]
    cpt_curves.add_header_column_to_data("dist")
    cpt_curves.data["fs"] *= -1
    cpt_curves.data["qc"] += cpt_curves.data["dist"]
    cpt_curves.data["fs"] += cpt_curves.data["dist"]
    return cpt_curves
