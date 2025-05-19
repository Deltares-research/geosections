# Configuration.toml

All information that is plotted in a cross-section is passed through a .toml configuration file.
This contains among other the general settings, input data and styling information of the section.
A `geosections` configuration TOML can contain the sections which are explained below. For every
possible option in each section, see the [configuration options](./options.md)

## Settings

```toml
[settings]
column_width = 20
fig_width = 11
fig_height = 7
inches = true
grid = true
```

## Line

```toml
[line]
file = "./cross_section_lines.geoparquet"       # Also accepts .shp files
crs = 28992
name = "E-W"
name_column = "name"
```

## Borehole data

```toml
[data.boreholes]
file = "./boreholes.parquet"                    # Also accepts .csv file
max_distance_to_line = 120
additional_nrs = ['B48B0396', 'B48B0398']
label = false                                   # Disable text labels
```

## CPT data

```toml
[data.cpts]
file = "./cpt_data.parquet"                     # Also accepts .csv file
max_distance_to_line = 30
crs = 4258
additional_nrs = ['CPT000000244400']
label = true
```

## CPT curves

```toml
[data.curves]
nrs = [
    "CPT000000050791",
    "CPT000000008329",
]
dist_scale_factor = 80
```

## Plot surfaces

Note the double brackets which make each "surface" entry part of a list to iterate over

```toml
[[surface]] 
file = "./ahn.tif"
style_kwds = { color = "k", linewidth = 0.5, label =  "Present surface" }

[[surface]]
file = "./basis_holoceen.img"
style_kwds = { color = "r", linestyle = "--", label =  "Holocene base (GeoTOP)" }
```

## Cross-section labels

```toml
[labels]
title = ""
xlabel = "Distance (m)"
ylabel = "Depth (NAP)"
```

## Lithology colors

```toml
[colors]
Z = "gold"
Kz = "yellowgreen"
K = "green"
Kh = "peru"
V = "brown"
L = "yellowgreen"
G = "orange"
```
