
import numpy as np
import matplotlib as mpl
import seaborn as sns

from matplotlib.colors import ListedColormap


main_colors = [
    (35, 85, 140),      # main
    (170, 135, 120),    # 2
    (189, 190, 196),    # 3
    (225, 105, 75),     # 4
    (0, 0, 0),          # 5
    (145, 146, 156)     # 6
]
main_colors = np.array(main_colors) / 255
main_colors = [mpl.colors.to_rgba(c) for c in main_colors]


def lighten(c, a):
    """
    turn color (r, g, b, x) to (r, g, b, a)
    """
    return tuple(list(mpl.colors.to_rgb(c)) + [a])


secondary_colors = [lighten(c, 0.6) for c in main_colors[:4]]


SG_COLORS_MATPLOTLIB = main_colors + secondary_colors

SG_THEME_HIGHCHARTS = {
    'colors':
        [mpl.colors.to_hex(e) for e in SG_COLORS_MATPLOTLIB[:6]] + \
        # the 4 original colors are the same rgb - only opacity changes
        # so created 4 new colors with https://www.sessions.edu/color-calculator/
        ['#667ba8', '#b799b4', '#c4c3bd', '#c87d6b']
}

CMAP_SG_BuRd = sns.diverging_palette(
    248, 23, s=70.4, l=40, center='light', as_cmap=True)
CMAP_SG_RdBu = sns.diverging_palette(
    23, 248, s=70.4, l=40, center='light', as_cmap=True)
CMAP_SG_White = ListedColormap(['white'])
