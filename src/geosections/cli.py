import typer
from rich import print

from geosections import check, plotting

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
    plotting.plot_cross_section(config, output_file, close)


@app.command()
def unique_lithologies(
    config: str = typer.Argument(..., help="Pad naar TOML-configuratiebestand")
):
    """
    Print unique lithologies present in the boreholes and CPTs that are shown in a
    cross-section.

    """
    uniques = check.check_lithology(config)
    print(f"Unique lithologies in boreholes: [yellow]{sorted(uniques)}[/yellow]\n")


if __name__ == "__main__":
    app()
