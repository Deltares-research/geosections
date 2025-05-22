from geosections import read


def check_lithology(config):
    config = read.read_config(config)
    line = read.read_line(config.line)
    boreholes = read.read_boreholes(config.data.boreholes, line)
    cpts = read.read_cpts(config.data.cpts, line)
    return set(boreholes.data["lith"]) | set(cpts.data["lith"])
