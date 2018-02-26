__author__ = 'maximmillen'

import pickle

from bwplot import cbox

import engformat.plot_tools as tools
import matplotlib.pyplot as plt

from matplotlib import rc
rc('font', family='Times New Roman', size=10)
import matplotlib


def journal_figure(fig, figure_path, size="small"):
    fig.set_size_inches(4, 4)

    fig.savefig(figure_path, dpi=100)


def time_series(sp, **kwargs):
    balance = kwargs.get('balance', False)
    origin = kwargs.get('origin', True)
    sp.yaxis.grid(True)
    tools.clean_chart(sp)
    if origin:
        sp.plot(sp.get_xlim(), [0, 0], c=cbox('dark gray'), ls='--', zorder=-1, lw=0.7)
    if balance:
        ylim = max(abs(sp.get_ylim()[0]), abs(sp.get_ylim()[1]))
        sp.set_ylim([-ylim, ylim])
    sp.tick_params(axis="both", which="both", bottom="on", top="off",
                labelbottom="on", left="off", right="off", labelleft="on")
    tools.trim_ticks(sp, balance=balance)
    if balance:
        ylim = max(abs(sp.get_ylim()[0]), abs(sp.get_ylim()[1]))
        sp.set_ylim([-ylim, ylim])


def new_time_series_plots(nrows=1):

    bf, sub_plots = plt.subplots(nrows=nrows, ncols=1, sharex=True)
    for sp in sub_plots:
        sp.tick_params(axis="both", which="both", bottom="off", top="off",
                labelbottom="off", left="off", right="off", labelleft="on")
    sub_plots[-1].tick_params(axis="both", which="both", bottom="on", top="off",
                labelbottom="on", left="off", right="off", labelleft="on")
    return sub_plots


def time_series_plots(sub_plots):

    for sp in sub_plots:
        sp.tick_params(axis="both", which="both", bottom="off", top="off",
                labelbottom="off", left="off", right="off", labelleft="on")
        sp.set_xlabel("")
    sub_plots[-1].tick_params(axis="both", which="both", bottom="on", top="off",
                labelbottom="on", left="off", right="off", labelleft="on")
    return sub_plots


def xy(sp, **kwargs):
    matplotlib.rcParams['lines.linewidth'] = 1.2
    x_origin = kwargs.get('x_origin', False)
    y_origin = kwargs.get('y_origin', False)
    x_axis = kwargs.get('x_axis', False)
    y_axis = kwargs.get('y_axis', False)
    parity = kwargs.get('parity', False)
    x_grid = kwargs.get('x_grid', True)
    y_grid = kwargs.get('y_grid', True)
    ratio = kwargs.get('ratio', False)
    if x_grid:
        sp.yaxis.grid(True, c=cbox('light gray'), zorder=-5, ls="--")
    if y_grid:
        sp.xaxis.grid(True, c=cbox('light gray'), zorder=-6, ls="--")
    tools.clean_chart(sp)
    sp.tick_params(axis="both", which="both", bottom="on", top="off",
                   labelbottom="on", left="on", right="off", labelleft="on")
    xlim = sp.get_xlim()
    ylim = sp.get_ylim()
    if x_origin:
        sp.set_xlim([0, xlim[1]])
    if y_origin:
        sp.set_ylim([0, ylim[1]])
    xlim = sp.get_xlim()
    ylim = sp.get_ylim()
    if x_axis:
        sp.plot([-xlim[1], xlim[1]], [0, 0], c=cbox('dark gray'), zorder=-1)
    if y_axis:
        sp.plot([0, 0], [-ylim[1], ylim[1]], c=cbox('dark gray'), zorder=-2)
    if ratio:
        sp.plot(xlim, [1, 1], c=cbox('dark gray'), zorder=-3)
    if parity:
        botlim = min(xlim[0], ylim[0])
        toplim = min(xlim[1], ylim[1])
        sp.plot([botlim, toplim], [botlim, toplim], c=cbox('mid gray'), zorder=-2)
        if parity == 2:
            sp.fill_between([botlim, toplim], [botlim, 0.5 * toplim], [botlim, 2 * toplim], facecolor=cbox('mid gray'), zorder=-3, alpha=0.1)
            # sp.plot([0, minlim], [0, 0.5 * minlim], c=cbox('mid gray'), zorder=-2)


def rotation_settlement(sp):
    sp.yaxis.grid(True)
    sp.xaxis.grid(True)
    tools.clean_chart(sp)
    xlim = max(abs(sp.get_xlim()[0]), abs(sp.get_xlim()[1]))
    sp.set_xlim([-xlim, xlim])
    sp.set_ylim([(sp.get_ylim()[0]), (sp.get_ylim()[1])])
    # plot origin
    sp.plot([-xlim, xlim], [0, 0], c=cbox('dark gray'), zorder=-1)
    sp.plot([0, 0], [(sp.get_ylim()[0]), (sp.get_ylim()[1])], c=cbox('dark gray'), zorder=-2)
    sp.tick_params(axis="both", which="both", bottom="on", top="off",
                   labelbottom="on", left="on", right="off", labelleft="on")


def hysteresis(sp):
    sp.yaxis.grid(True)
    sp.xaxis.grid(True)
    tools.clean_chart(sp)
    ylim = max(abs(sp.get_ylim()[0]), abs(sp.get_ylim()[1]))
    sp.set_ylim([-ylim, ylim])
    xlimits = sp.get_xlim()
    xlims = [0, 0]
    for x in range(len(xlimits)):
        if abs(xlimits[x]) > 0.999 and abs(xlimits[x]) < 1.0001:
            xlims[x] = 0
            print('found culprit')
        else:
            xlims[x] = xlimits[x]
    print('xlims: ', xlims)
    xlim = max(abs(xlims[0]), abs(xlims[1]))
    sp.set_xlim([-xlim, xlim])
    # plot origin
    sp.plot([-xlim, xlim], [0, 0], c=cbox('dark gray'), zorder=-1)
    sp.plot([0, 0], [-ylim, ylim], c=cbox('dark gray'), zorder=-2)
    sp.tick_params(axis="both", which="both", bottom="on", top="off",
                labelbottom="on", left="on", right="off", labelleft="on")


def transfer_function(sp, **kwargs):
    """
    Prepare a transfer function plot
    :param sp:
    :param kwargs:
    :return:
    """

    x_grid = kwargs.get('x_grid', True)
    y_grid = kwargs.get('y_grid', True)
    ratio = kwargs.get('ratio', False)

    if x_grid:
        sp.yaxis.grid(True, c=(0.9, 0.9, 0.9))
    if y_grid:
        sp.xaxis.grid(True, c=(0.9, 0.9, 0.9))

    lines = sp.get_lines()
    for line in lines:
        z_value = line.get_zorder()
        line.set_zorder(z_value + 100)
    tools.clean_chart(sp)
    sp.tick_params(axis="both", which="both", bottom="on", top="off",
                   labelbottom="on", left="on", right="off", labelleft="on")
    xlim = sp.get_xlim()
    ylim = sp.get_ylim()
    # set to xy origin:
    sp.set_xlim([0, xlim[1]])
    sp.set_ylim([0, ylim[1]])

    if ratio:
        xlim = sp.get_xlim()
        sp.plot(xlim, [1, 1], c=cbox('dark gray'), lw=0.7, zorder=50)


def save_plot_state(sub_plot, name):
    from pathlib import Path
    home = str(Path.home())
    with open(home + '/esfp_files/%s.pkl' % name, 'wb') as fid:
        pickle.dump(sub_plot, fid)


def load_plot_state(name):
    from pathlib import Path
    home = str(Path.home())
    with open(home + '/esfp_files/%s.pkl' % name, 'rb') as fid:
        ax = pickle.load(fid)
    return ax