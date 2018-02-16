import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.tools as plyt
from utils import diff_month


def plot_dataframe(df_to_plot, pdf, height=None, width=None, title="Dataset"):
    """
    Plot dataframes of data.
    :param df_to_plot: pandas.DataFrame
        dataframe to plot
    :param pdf: PDFobject or string
        file where the plot will be stored
    :param height: int
        height of the plot
    :param width: int
        width of the plot
    :param title: string
        title of the plot
    """
    height = 3 * len(df_to_plot.columns) if height is None else height
    width = 1 + 0.2 * len(df_to_plot) if width is None else width

    fig = plt.figure(figsize=(height, width))

    plt.axis('tight')
    plt.axis('off')
    plt.table(cellText=df_to_plot.values, colWidths=[0.5] * len(df_to_plot.columns),
              colLabels=df_to_plot.columns,
              cellLoc='center', rowLoc='center', loc='center')
    plt.title(title)
    plt.tight_layout()

    fig.savefig(pdf, format="pdf")


def plot_timeseries(series, names_series, pdf, series_labels=None, series_outliers=None, series_negatives=None,
                    ylabel="Value", title="Time series plot"):
    """
    Plot high frequency time series of data.
    :param series: pandas.Series of List of pandas.Series with DateTime index.
        the time series which will be drawn in the plot.
    :param names_series: list of strings
        the names of the series. In the same order to the series list.
    :param pdf: PDFobject or string
        file where the plot will be stored
    :param series_labels: pandas.Series with datetime index
        This series will be represented by labels painted on the main series, so is recommended to contain very few items.
    :param series_outliers: pd.Series with datetime index and Boolean values
         If true, that element is an outlier
    :param series_negatives:
        Boolean Pandas series with datetime index
        If true, that element is negative.
    :param ylabel: str
        The Y axis label name
    :param title: str
        Title of the plot
    :return:
    """

    if isinstance(series,list):
        max_series = max(series[0].index)
        min_series = min(series[0].index)
        for i in series:
            max_series = max(i.index) if max_series<max(i.index) else max_series
            min_series = min(i.index) if min_series>min(i.index) else min_series
    else:
        max_series = max(series.index)
        min_series = min(series.index)

    fig = plt.figure(figsize=[(abs(diff_month(max_series,min_series)) * 3) + 20, 4])

    ax = plt.gca()
    ax.grid(True)
    if isinstance(series,list):
        for i in xrange(series):
            ax.plot(series[i], label=names_series[i], linewidth=2.5)
    else:
        name_label = names_series[0] if isinstance(names_series,list) else names_series
        ax.plot(series, label=name_label, linewidth=2.5)

    if series_labels is not None:
        for i in xrange(len(series_labels)):
            text = "Reading={:.3f}".format(series_labels[i])
            bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.03)
            # arrowprops = dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=60")
            kw = dict(xycoords='data', textcoords="axes fraction", bbox=bbox_props, ha="right", va="top")
            ax.annotate(text, xy=(mdates.date2num(series_labels.index[i]), series.quantile(1)), bbox=bbox_props)

    if series_outliers is not None:
        outliers_=pd.Series(np.where(series_outliers == True, (max(series)-min(series))*0.9+min(series), min(series)),
                            series_outliers.index)
        #ax.plot(pd.Series(np.where(series_outliers == True, max(series),min(series)),series_outliers.index), label="outliers",linewidth=0.3)
        ax.plot(outliers_[outliers_>min(series)],'rx',
                label="outliers", markersize=8)

    if series_negatives is not None:
        negatives_=pd.Series(np.where(series_negatives == True, (max(series)-min(series))*0.8+min(series),min(series)),
                             series_negatives.index)
        #ax.plot(pd.Series(np.where(series_negatives == True,max(series),min(series)),series_negatives.index), label="negatives",linewidth=0.3)
        ax.plot(negatives_[negatives_>min(series)],'gx',
                label="negatives", markersize=8)

    ax.set_ylabel(ylabel)
    plt.legend(bbox_to_anchor=(0.95, 1), loc=2,
               borderaxespad=0.)

    plt.title(title)
    plt.tight_layout()

    fig.savefig(pdf, format="pdf")


def plot_histogram(series, pdf, title="Histogram"):
    """
    Plot histogram of a series.
    :param series: Pandas series object
    :param pdf: PDF object or PDF filename where the plot will be stored
    :param title: Title of the plot
    :return:
    """
    fig = plt.figure(figsize=[10, 5])

    histdata = series.reset_index().value
    histdata.plot.hist(bins=100)
    plt.title(title)
    plt.tight_layout()

    fig.savefig(pdf, format="pdf")


def initialize_plotly_by_rows(nrows, titles):
    return plyt.make_subplots(rows=nrows, cols=1, shared_xaxes=True, subplot_titles=titles)


def add_plotly_timeseries(fig, series, deviceId, type, unit):
    element = len(fig['data']) + 1
    fig.append_trace(
        go.Scatter(
            x=series.index,
            y=series,  # assign x as the dataframe column 'x'
            name="%s-%s" % (deviceId, type),
            hoverlabel={"namelength": 30}
        ), element, 1)
    fig['layout']['xaxis'].update(title="time")
    fig['layout']['yaxis%s' % str(element)].update(title=unit)
    return fig
