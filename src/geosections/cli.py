import typer
from matplotlib import pyplot as plt

from geosections import plotting, read

app = typer.Typer()


@app.command()
def plot(
    config: str = typer.Argument(..., help="Path to TOML-configuration file"),
    output_file: str = typer.Option(None, "--save", help="Path to output file"),
    close: bool = typer.Option(False, "--close", help="Close plot"),
):
    config = read.read_config(config)
    line = read.read_line(config.line)

    fig, ax = plt.subplots(
        figsize=(config.settings.fig_width, config.settings.fig_height),
        tight_layout=config.settings.tight_layout,
    )

    if config.data.boreholes is not None:
        boreholes = read.read_boreholes(config.data.boreholes, line)
        plotting.plot_borehole_data(
            ax, boreholes, config.colors, config.settings.column_with
        )

    if config.data.cpts is not None:
        cpts = read.read_cpts(config.data.cpts, line)
        plotting.plot_borehole_data(
            ax, cpts, config.colors, config.settings.column_with
        )

    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin - 2, ymax)
    ax.set_xlim(0, line.length)
    ax.set_xlabel(config.labels.xlabel)
    ax.set_ylabel(config.labels.ylabel)
    ax.set_title(config.labels.title)
    ax.grid(config.settings.grid, linestyle="--", alpha=0.5)

    if config.data.curves is not None:
        curves = read.read_curves(config, line)
        plotting.plot_curves(ax, curves, ymax)

    if config.surface:
        for surface in config.surface:
            surface_line = read.read_surface(surface, line)
            ax.plot(
                surface_line["dist"].values, surface_line.values, **surface.style_kwds
            )

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
    config = read.read_config(config)
    line = read.read_line(config.line)
    boreholes = read.read_boreholes(config.data.boreholes, line)
    cpts = read.read_cpts(config.data.cpts, line)

    uniques = set(boreholes.data["lith"]) | set(cpts.data["lith"])
    typer.secho(
        f"Unique lithologies in boreholes: {uniques}",
        fg=typer.colors.BLUE,
    )
