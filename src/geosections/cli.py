import tomllib

import typer
from matplotlib import pyplot as plt

from geosections import read

app = typer.Typer()


@app.command()
def plot(
    config: str = typer.Argument(..., help="Path to TOML-configuration file"),
    output_file: str = typer.Option(None, "--save", help="Path to output file"),
    show: bool = typer.Option(True, "--dont-show", help="Do not show plot"),
):
    with open(config, "rb") as f:
        config = tomllib.load(f)

    plt.plot(config["x"], config["y"])
    plt.xlabel(config["xlabel"])
    plt.ylabel(config["ylabel"])
    plt.grid()
    if output_file:
        plt.savefig(output_file)
    if show:
        plt.show()
    plt.close()


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
