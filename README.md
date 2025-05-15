# Geosections (experimental)

[![PyPI version](https://img.shields.io/pypi/v/geosections.svg)](https://pypi.org/project/geosections)
[![License: MIT](https://img.shields.io/pypi/l/imod)](https://choosealicense.com/licenses/mit)
[![Lifecycle: experimental](https://lifecycle.r-lib.org/articles/figures/lifecycle-experimental.svg)](https://lifecycle.r-lib.org/articles/stages.html)
[![Build: status](https://img.shields.io/github/actions/workflow/status/deltares-research/geosections/ci.yml)](https://github.com/Deltares-research/geosections/actions)
[![codecov](https://codecov.io/gh/Deltares-research/geosections/graph/badge.svg?token=HCNGLWTQ2H)](https://codecov.io/gh/Deltares-research/geosections)
[![Formatting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/charliermarsh/ruff)

Simple command line tool to create geological cross-sections from borehole and CPT data
using `.toml` configuration files.

## Installation

Install the latest release by:

```powershell
pip install geosections
```

Or the latest (experimental) version of the main branch directly from GitHub using:

```powershell
pip install git+https://github.com/Deltares-research/geosections.git
```

## Usage

Every element that needs to plotted in a section is specified in a configuration `.toml`.
Below is a simple example `.toml` that plots borehole data from a `.parquet` file and a
AHN surface along a section line:

```toml
[settings] # General plot settings
column_width = 20 # Width of boreholes
fig_width = 11
fig_height = 7
grid = true

[line]
file = "my_line.shp"
crs = 28992 # Geosections uses this crs as default

[data.boreholes]
file = "my_boreholes.parquet"
max_distance_to_line = 50 # Meters

[[surface]]
file = "ahn_surface.tif"
style_kwds = { color = "r", label = "AHN surface" } # Matplotlib keyword arguments

[labels]
xlabel = "Distance (m)"
ylabel = "Depth (NAP)"

[colors]
Z = "gold"
K = "green"
V = "brown"
```

Next, create the cross-section by:

```powershell
geosections plot my_settings.toml --save "my-section.png"
```
