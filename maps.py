from matplotlib import pyplot as plt
import matplotlib.colors
import seaborn as sns
import numpy as np

# fmt: off
LABELS_MAHJONG_TILES = [
    "1 man", "2 man", "3 man", "4 man", "5 man", "6 man", "7 man", "8 man", "9 man",
    "1 pin", "2 pin", "3 pin", "4 pin", "5 pin", "6 pin", "7 pin", "8 pin", "9 pin",
    "1 sou", "2 sou", "3 sou", "4 sou", "5 sou", "6 sou", "7 sou", "8 sou", "9 sou",
    "East", "South", "West", "North", "Haku", "Hatsu", "Chun",
]

LABELS_Y = [
    "Metadata", "Dora indicators", "POV hand",
    "P0 melds", "P1 melds", "P2 melds", "P3 melds",
    "P0 pool", "P1 pool", "P2 pool", "P3 pool",
    "P0 discards", "P1 discards", "P2 discards", "P3 discards",
]

LABELS_METADATA = (
    ["Round wind", "Dealer", "POV player", "# honba sticks", "# riichi sticks", "# wall tiles"]
    + [f"P{i} score" for i in range(4)]
    + [f"P{i} riichi" for i in range(4)]
    + ["Padding" for _ in range(18)]
    + ["Round Number", "Step Number"]
)

KAGGLE_MAHJONG_COLORMAP = {
    "norm": matplotlib.colors.BoundaryNorm([-128, 0, 1, 2, 3, 4, 5, 128], 8),
    "cmap": sns.color_palette(["#000000", "#ffffff", "#bf3100", "#da7c00", "#FFC312", "#ffd64f", "#ff7979"]),
}
# fmt: on


def generate_mahjong_heatmap(
    input_matrix: np.ndarray,
    title: str = "",
    output_path=None,
    show_fig=True,
):
    """Generates and displays a simplified heatmap for a mahjong game state matrix."""
    assert input_matrix.ndim == 2, "Method expects a 2D matrix!"

    # Usar valores fijos 
    labels_top = LABELS_METADATA
    labels_bottom = LABELS_MAHJONG_TILES
    labels_left = LABELS_Y
    figure_size = (18, 11)
    colormap = "kaggle_mahjong"
    
    fig, ax_heatmap = plt.subplots(figsize=figure_size)

    # Parámetros del heatmap con valores fijos
    heatmap_params = {
        "ax": ax_heatmap,
        "annot": True,
        "fmt": "g",
        "square": True,
        "xticklabels": labels_bottom,
        "yticklabels": labels_left,
        "annot_kws": {"fontsize": 11},
        "robust": True,
        "cbar": False,
        "linewidths": 2,  # Borde fijo
        "linecolor": "black",  # Color de borde fijo
    }

    # Aplicar colormap fijo de kaggle_mahjong
    heatmap_params.update(KAGGLE_MAHJONG_COLORMAP)

    ax_seaborn = sns.heatmap(input_matrix, **heatmap_params)

    ax_seaborn.tick_params(left=False, bottom=False, top=False, labelsize=12)
    if title:
        ax_seaborn.set_title(title, fontdict={"fontsize": 20})

    # Agregar etiquetas en la parte superior
    secax = ax_seaborn.secondary_xaxis("top")
    secax.set_xticks(ax_seaborn.get_xticks())
    secax.set_xticklabels(labels_top, rotation=90, fontsize=12)
    secax.tick_params(axis="x", which="both", length=0)

    fig.tight_layout()

    if output_path:
        plt.savefig(f"{output_path}.png", bbox_inches="tight")

    if show_fig:
        plt.show()