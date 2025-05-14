# Command line tools

This is an explanation of the command line tools

Create a cross-section from a .toml file:
```powershell
geosections plot my_settings.toml --save "my-section.png"
```

Check each unique lithology code that is present in the data in the cross-section to configure a legend:
```powershell
geosections check-unique-lithologies my_settings.toml
```