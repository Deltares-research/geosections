import re


def plot_borehole_data(ax, data, colors, label, width=20):
    for nr, dist in zip(data.header["nr"], data.header["dist"]):
        c = data.data[data.data["nr"] == nr]
        plot_borehole(ax, c, dist, width, colors)

        # Label the borehole if labelling is enabled
        if label:
            plot_label(ax, nr, dist)
    return


def plot_borehole(ax, df, dist, width, colors):
    df["top"] = df["surface"] - df["top"]
    df["bottom"] = df["surface"] - df["bottom"]

    thickness = df["top"] - df["bottom"]
    for lith, t, bot in zip(df["lith"], thickness, df["bottom"]):
        ax.bar(dist, t, bottom=bot, color=colors.get(lith, "grey"), width=width)
    return


def plot_curves(ax, curves, label):
    for nr in curves.header["nr"]:
        c = curves.get(nr)
        ax.plot(c.data["qc"], c.data["depth"], color="r", linewidth=0.5)
        ax.plot(c.data["fs"], c.data["depth"], color="b", linewidth=0.5)

        # Label the curve if labelling is enabled
        if label:
            plot_label(ax, nr, c.header["dist"])
    return


def plot_label(ax, label, dist):
    ax.text(
        dist,
        1.01,
        re.sub(r"0{5,}", "", label),
        rotation=90,
        ha="center",
        va="bottom",
        fontsize=8,
        transform=ax.get_xaxis_transform(),
    )
