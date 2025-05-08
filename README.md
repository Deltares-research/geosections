# Geosections (experimental)

Simple command line tool to create geological cross-sections from borehole and CPT data
using `.toml` configuration files.


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