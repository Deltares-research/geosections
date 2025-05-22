import re

import matplotlib.pyplot as plt
from rich import print

from geosections import read


def plot_cross_section(config, output_file, close):
    config = read.read_config(config)
    line = read.read_line(config.line)

    fig_width = config.settings.fig_width
    fig_height = config.settings.fig_height
    if not config.settings.inches:
        fig_width /= 2.54
        fig_height /= 2.54

    fig, ax = plt.subplots(
        figsize=(fig_width, fig_height), tight_layout=config.settings.tight_layout
    )

    if config.data.boreholes is not None:
        print(f"Plotting boreholes from [blue]{config.data.boreholes.file.name}[/blue]")
        boreholes = read.read_boreholes(config.data.boreholes, line)
        plot_borehole_data(
            ax,
            boreholes,
            config.colors,
            config.data.boreholes.label,
            config.settings.column_width,
        )

    if config.data.cpts is not None:
        print(f"Plotting CPTs from [blue]{config.data.cpts.file.name}[/blue]")
        cpts = read.read_cpts(config.data.cpts, line)
        plot_borehole_data(
            ax,
            cpts,
            config.colors,
            config.data.cpts.label,
            config.settings.column_width,
        )

    if config.data.curves is not None:
        print(f"Plotting curves from [blue]{config.data.curves.nrs}[/blue]")
        curves = read.read_curves(config.data.curves, line)
        plot_curves(ax, curves, config.data.curves.label)

    if config.surface:
        for surface in config.surface:
            print(f"Plotting surface from [blue]{surface.file.name}[/blue]")
            surface_line = read.read_surface(surface, line)
            ax.plot(
                surface_line["dist"].values, surface_line.values, **surface.style_kwds
            )

    ymin, ymax = ax.get_ylim()
    ymin = ymin if config.settings.ymin is None else config.settings.ymin
    ymax = ymax if config.settings.ymax is None else config.settings.ymax

    xmin = 0 if config.settings.xmin is None else config.settings.xmin
    xmax = line.length if config.settings.xmax is None else config.settings.xmax

    ax.set_ylim(ymin, ymax)
    ax.set_xlim(xmin, xmax)
    ax.set_xlabel(config.labels.xlabel)
    ax.set_ylabel(config.labels.ylabel)
    ax.set_title(config.labels.title)
    ax.grid(config.settings.grid, linestyle="--", alpha=0.5)

    if output_file:
        fig.savefig(output_file)

    if close:
        plt.close()
    else:
        plt.show()


def plot_borehole_data(ax, data, colors, label, width=20):
    for nr, dist in zip(data.header["nr"], data.header["dist"]):
        c = data.data[data.data["nr"] == nr]
        plot_borehole(ax, c, dist, width, colors)

        # Label the borehole if labelling is enabled
        if label:
            plot_label(ax, nr, dist)
    return


def plot_borehole(ax, df, dist, width, colors):
    df["top"] = df["surface"] - df["top"]
    df["bottom"] = df["surface"] - df["bottom"]

    thickness = df["top"] - df["bottom"]
    for lith, t, bot in zip(df["lith"], thickness, df["bottom"]):
        ax.bar(dist, t, bottom=bot, color=colors.get(lith, "grey"), width=width)
    return


def plot_curves(ax, curves, label):
    for nr in curves.header["nr"]:
        c = curves.get(nr)
        ax.plot(c.data["qc"], c.data["depth"], color="r", linewidth=0.5)
        ax.plot(c.data["fs"], c.data["depth"], color="b", linewidth=0.5)

        # Label the curve if labelling is enabled
        if label:
            plot_label(ax, nr, c.header["dist"])
    return


def plot_label(ax, label, dist):
    ax.text(
        dist,
        1.01,
        re.sub(r"0{5,}", "", label),
        rotation=90,
        ha="center",
        va="bottom",
        fontsize=8,
        transform=ax.get_xaxis_transform(),
    )
