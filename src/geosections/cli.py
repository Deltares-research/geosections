import typer
from matplotlib import pyplot as plt
from rich import print

from geosections import plotting, read, utils

app = typer.Typer()


@app.command()
def plot(
    config: str = typer.Argument(..., help="Path to TOML-configuration file"),
    output_file: str = typer.Option(None, "--save", help="Path to output file"),
    close: bool = typer.Option(False, "--close", help="Close plot"),
):
    """
    Create a cross-section plot from borehole and CPT data based on a .toml configuration
    file containing input data and plot settings.

    """
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
        print(
            f"Plotting boreholes from [blue]{utils.get_filename(config.data.boreholes.file)}[/blue]"
        )
        boreholes = read.read_boreholes(config.data.boreholes, line)
        plotting.plot_borehole_data(
            ax,
            boreholes,
            config.colors,
            config.data.boreholes.label,
            config.settings.column_with,
        )

    if config.data.cpts is not None:
        print(
            f"Plotting CPTs from [blue]{utils.get_filename(config.data.cpts.file)}[/blue]"
        )
        cpts = read.read_cpts(config.data.cpts, line)
        plotting.plot_borehole_data(
            ax,
            cpts,
            config.colors,
            config.data.cpts.label,
            config.settings.column_with,
        )

    if config.data.curves is not None:
        print(f"Plotting curves from [blue]{config.data.curves.nrs}[/blue]")
        curves = read.read_curves(config, line)
        plotting.plot_curves(ax, curves, config.data.curves.label)

    if config.surface:
        for surface in config.surface:
            print(
                f"Plotting surface from [blue]{utils.get_filename(surface.file)}[/blue]"
            )
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


@app.command()
def check_unique_lithologies(
    config: str = typer.Argument(..., help="Pad naar TOML-configuratiebestand")
):
    """
    Print unique lithologies present in the boreholes and CPTs that are shown in a
    cross-section.

    """
    config = read.read_config(config)
    line = read.read_line(config.line)
    boreholes = read.read_boreholes(config.data.boreholes, line)
    cpts = read.read_cpts(config.data.cpts, line)

    uniques = set(boreholes.data["lith"]) | set(cpts.data["lith"])
    print(f"Unique lithologies in boreholes: [yellow]{sorted(uniques)}[/yellow]\n")


if __name__ == "__main__":
    plot("test.toml", None, False)
    app()
