import tomllib
from pathlib import Path

import typer

from geosections import Config


def read_config(file: str | Path) -> Config:
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
        config = Config(**config)
    except Exception as e:
        typer.secho(f"Invalid configuration:\n{e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    return config


if __name__ == "__main__":
    config = read_config("test.toml")
    print(config)
