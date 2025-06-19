from matplotlib import pyplot as plt
import matplotlib.colors
import seaborn as sns
import numpy as np

# fmt: off
LABELS_MAHJONG_TILES = [
    "1 man", "2 man", "3 man",
    "4 man", "5 man", "6 man",
    "7 man", "8 man", "9 man",
    "1 pin", "2 pin", "3 pin",
    "4 pin", "5 pin", "6 pin",
    "7 pin", "8 pin", "9 pin",
    "1 sou", "2 sou", "3 sou",
    "4 sou", "5 sou", "6 sou",
    "7 sou", "8 sou", "9 sou",
    "East", "South", "West", "North",
    "Haku", "Hatsu", "Chun",
]

LABELS_Y = [
    "Metadata",
    "Dora indicators",
    "POV hand",
    "P0 melds", "P1 melds", "P2 melds", "P3 melds",
    "P0 pool", "P1 pool", "P2 pool", "P3 pool",
    "P0 discards", "P1 discards", "P2 discards", "P3 discards",
]

LABELS_METADATA = (
    [
        "Round wind",
        "Dealer",
        "POV player",
        "# honba sticks",
        "# riichi sticks",
        "# wall tiles",
    ]
    + ["P0 score", "P1 score", "P2 score", "P3 score"]
    + ["P0 riichi", "P1 riichi", "P2 riichi", "P3 riichi"]
    + ["Padding" for _ in range(18)]
    + ["Round Number", "Step Number"]
)

KAGGLE_MAHJONG_COLORMAP = {
    "norm": matplotlib.colors.BoundaryNorm([-128, 0, 1, 2, 3, 4, 5, 128], 8),
    "cmap": sns.color_palette(
        ["#000000", "#ffffff", "#bf3100", "#da7c00", "#FFC312", "#ffd64f", "#ff7979"]
    )
}
# fmt: on


def generate_mahjong_heatmap(
    input_matrix: np.ndarray,
    labels_left: list[str] | None = None,
    labels_top: list[str] | None = None,
    labels_bottom: list[str] | None = None,
    override_heatmap_params={},
    figure_size=(18, 11),
    title: str = "",
    enable_color_bar=False,
    color_bar_label: str = "",
    colormap="icefire",
    enable_annotation=True,
    enable_border=True,
    border_color="black",
    border_width=2,
    annotation_fontsize=11,
    label_fontsize=12,
    output_path=None,
    show_fig=True,
):
    """Generate a heatmap using the given input matrix.

    Args:
        input_matrix (np.ndarray): The input 2D array for heatmap generation.
        labels_left (list[str] | None, optional): Labels for the left side of the heatmap. If None, use default labels. If empty list, no labels are used.. Defaults to None.
        labels_top (list[str] | None, optional): Labels for the top side of the heatmap. If None, use default labels. If empty list, no labels are used.. Defaults to None.
        labels_bottom (list[str] | None, optional): Labels for the bottom side of the heatmap. If None, use default labels. If empty list, no labels are used.. Defaults to None.
        override_heatmap_params (dict, optional): _description_. Defaults to {}.
        figure_size (tuple, optional): Defaults to (18, 11).
        title (str, optional): Defaults to "".
        enable_color_bar (bool, optional): Defaults to False.
        color_bar_label (str, optional): Color bar label. Defaults to "".
        colormap (str, optional): _description_. Defaults to "icefire".
        enable_annotation (bool, optional): _description_. Defaults to True.
        enable_border (bool, optional): Enable border around the heatmap cells. Defaults to True.
        border_color (str, optional): Heatmap cell border color. Defaults to "black".
        border_width (int, optional): Heatmap cell border width. Defaults to 2.
        annotation_fontsize (int, optional): Heatmap cell annotation fontsize. Defaults to 11.
        label_fontsize (int, optional): Label fontsize. Defaults to 12.
        output_path (_type_, optional): Where to output the figure. If None, does not output. Defaults to None.
        show_fig (bool, optional): Show figure if True, otherwise suppress display. Defaults to True.
    """

    assert input_matrix.ndim == 2, "Method expects a 2D matrix!"

    if labels_top is None:
        labels_top = LABELS_METADATA

    if labels_bottom is None:
        labels_bottom = LABELS_MAHJONG_TILES

    if labels_left is None:
        labels_left = LABELS_Y

    fig, (ax_heatmap, ax_colormap) = plt.subplots(
        nrows=2,
        figsize=figure_size,
        gridspec_kw={"height_ratios": [100, 1]},
    )

    # Reasonable default params
    heatmap_params = dict(
        ax=ax_heatmap,
        cmap=colormap,
        annot=enable_annotation,
        fmt="g",
        square=True,
        xticklabels=labels_bottom,
        yticklabels=labels_left,
        annot_kws={"fontsize": annotation_fontsize},
        robust=True,
        cbar=enable_color_bar,  # Turning the color bar invisible further down
        cbar_ax=ax_colormap,
        cbar_kws=dict(label=color_bar_label, orientation="horizontal"),
    )

    # Heatmap grid color and width
    if enable_border:
        heatmap_params.update(dict(linewidths=border_width, linecolor=border_color))
    else:
        heatmap_params.update(dict(linewidths=0))

    if colormap == "kaggle_mahjong":
        heatmap_params.update(KAGGLE_MAHJONG_COLORMAP)

    heatmap_params.update(override_heatmap_params)

    ax_seaborn = sns.heatmap(input_matrix, **heatmap_params)

    ax_seaborn.tick_params(
        left=False, bottom=False, top=False, labelsize=label_fontsize
    )
    if title:
        ax_seaborn.set_title(title, fontdict=dict(fontsize=20))

    if labels_top:
        secax = ax_seaborn.secondary_xaxis("top")
        secax.set_xticks(ax_seaborn.get_xticks())
        secax.set_xticklabels(labels_top, rotation=90, fontsize=label_fontsize)
        secax.tick_params(axis="x", which="both", length=0)

    fig.tight_layout()

    if not enable_color_bar:
        ax_colormap.set_visible(False)

    if output_path is not None:
        plt.savefig(output_path + ".png", bbox_inches="tight")

    if show_fig:
        plt.show()