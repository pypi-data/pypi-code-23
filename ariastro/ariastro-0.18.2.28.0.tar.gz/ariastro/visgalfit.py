import f311.filetypes as ft
import f311.explorer as ex
import matplotlib.pyplot as plt
import a99
import numpy as np
from .filegalfit import *

__all__ = ["VisGalfitFig", "draw_galfit_tiles"]


# TODO setup image size

class VisGalfitFig(ex.Vis):
    """Draw tiles: (INPUT, MODEL, RESIDUAL) x (bands)"""

    input_classes = (FileGalfit,)
    action = __doc__

    def _do_use(self, m):
        draw_galfit_tiles(m)
        plt.show()


# TODO move to project ariastro
def draw_galfit_tiles(filegalfit, image_width=1000, preprocessing=None):
    """Draws a new matplotilb figure and returns it

    The figure will contain  = 3*(number of bands) subplots

    Args:
        filegalfit: FileGalfit instance
        image_width=1000: image width in pixels
        preprocessing: function to perform some operations with the "pixels" aiming to improve
                       visualization. This function will receive a matrix (grayscale image)
                       as argument. The default for this argument will be a function that will
                       enhance small values:

            lambda image: np.power(image, 0.2)

    Returns:
        matplotlib figure
    """
    # TODO fine-tune axis positions (not with tight_layout())

    if preprocessing is None:
        preprocessing = lambda image: np.power(image, 0.2)

    num_rows = len(filegalfit.kind_names)
    num_cols = len(filegalfit.band_names)
    fig, axarr = plt.subplots(num_rows+1, num_cols, squeeze=False)
    for i, kind_name in enumerate(filegalfit.kind_names):
        for j, band_name in enumerate(filegalfit.band_names):
            ax = axarr[i, j]
            remove_ticks(ax)

            # Gets grayscale image data
            hdu = filegalfit.get_frame(kind_name, band_name)
            im = hdu.data

            # Clips negative values
            im[im < 0] =  0

            # Applies pre-processing to image
            image_data = preprocessing(im)

            # Plots image
            hei, wid = image_data.shape
            ax.imshow(image_data, cmap='gray')
            ax.set_ylim([0, hei - 1])
            ax.set_xlim([0, wid - 1])

            if i == 0:
                # First row, will indicate band on top
                ax.text(wid/2, hei+4, filegalfit.band_names[j],
                        horizontalalignment='center',
                        verticalalignment='bottom')

            if j == num_cols-1:
                # Last column, will write kind_name as rotated text at the right of the tile
                ax.text(wid+4, hei/2, filegalfit.kind_names[i],
                        horizontalalignment='left',
                        verticalalignment='center',
                        rotation=90)

    if True:
        for j, band_name in enumerate(filegalfit.band_names):
            ax = axarr[3, j]

            hdu = filegalfit.get_frame("MODEL", band_name)

            for x in ["top", "left", "right", "bottom"]:
                ax.spines[x].set_visible(False)
            # ax.set_box("off")
            remove_ticks(ax)

            im = hdu.data
            hei, wid = hdu.data.shape

            ax.set_ylim([0, hei - 1])
            ax.set_xlim([0, wid - 1])


            # Uses _REF_KEYWORD to look for number
            header_keys = list(hdu.header.keys())
            number = None
            _POSSIBLE_NUMBERS = [1, 2, 3]
            _REF_KEYWORD = "RE"
            for _number in _POSSIBLE_NUMBERS:
                search = "{}_RE".format(_number)
                for key in header_keys:
                    if search in key:
                        number = _number
                        a99.get_python_logger().info("Found keyword '{}', number is {}".format(key, number))
                        break
                if number:
                    break

            if not number:
                _bite = " nor ".join(["'{}_{}'".format(i, _REF_KEYWORD) for i in _POSSIBLE_NUMBERS])

                raise RuntimeError("Neither {} found as part of model header keywords".
                                   format(_bite))

            # Tries to collect data from headers with fallback in case the header information wanted are not present
            data = {}
            _map = {"RE": lambda: hdu.header["{}_RE_{}".format(number, band_name.upper())],
                    "N": lambda: hdu.header["{}_N_{}".format(number, band_name.upper())],
                    "RS": lambda: hdu.header["{}_RS_{}".format(number, band_name.upper())],
                    "CHI2NU": lambda: "\n\nCHI2NU={:g}".format(number, hdu.header["CHI2NU"]) if j == 0 else ""
                   }


            for key, function in _map.items():
                try:
                    data[key] = function()
                except KeyError as e:
                    a99.get_python_logger().warning("File '{}': {}".format(filegalfit.filename, str(e)))
                    data[key] = "?{}?".format(key)

            ax.text(2, hei - 1, "RE={RE}\nN={N}\nRS={RS}{CHI2NU}".format(**data),
                    horizontalalignment='left',
                    verticalalignment='top', fontsize=7, color='red',
                    bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 2})

    a99.set_figure_size(fig, image_width, image_width/num_cols*4)
    plt.tight_layout()


def remove_ticks(ax):
    # http://stackoverflow.com/questions/12998430/remove-xticks-in-a-matplot-lib-plot
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())

