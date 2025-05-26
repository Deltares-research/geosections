# Command line tools

Geosections contains two command line functions, one to plot a cross-section and another
to check the input data that will be plotted in a section, specifically which lithologies
are present in the data. Both functions take as input a TOML configuration file (e.g.
`my-settings.toml`) as input. See the [Configuration file](./configuration.md) and
[Configuration options](./options.md) sections for the structure and content of such a
TOML file.

## Check lithology in the data

A cross-section shows the lithologic composition of borehole and CPT data in specific colors per
lithology. These colors are specified in the configuration TOML (see [Colors](./configuration.md#lithology-colors)
section). Therefore, `geosections` has a `unique-lithologies` function to check the present
lithologic classes that are present in the data. Check each unique lithology code that is present
in the data in the cross-section to configure a legend by:

```powershell
geosections unique-lithologies "my_settings.toml"
```

## Creating a cross-section

Create a cross-section based on the TOML file by using:

```powershell
geosections plot "my_settings.toml"
```

This opens a plot window for the cross-section for inspecting the result. When the result
is good enough, the section can directly be saved by clicking the save icon in the window.
If the changes are required, simply close the plot window and type the same command.

The `plot` function also has options available to directly save the section, or close the
preview plot window. To directly save the plot to an output file use:

```powershell
geosections plot "my_settings.toml" --save "my-section.pdf"
```

Or directly save and do not show a preview:

```powershell
geosections plot "my_settings.toml" --save "my-section.pdf" --close
```
