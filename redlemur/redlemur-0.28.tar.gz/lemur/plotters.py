import os
import imageio
from PIL import ImageDraw, Image, ImageFont

from plotly.offline import iplot, plot
import plotly.graph_objs as go
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import hashlib
from ipywidgets import interact
import random
import scipy.signal as signal
import colorlover as cl

from nilearn import image as nimage
from nilearn import plotting as nilplot
import nibabel as nib

from lemur import embedders as leb
from .utils import qa_graphs as qg
from .utils import qa_graphs_plotting as qgp

def get_spaced_colors(n):
    max_value = 255
    interval = int(max_value / n)
    hues = range(0, max_value, interval)
    return cl.to_rgb(["hsl(%d,100%%,40%%)"%i for i in hues])

def get_heat_colors(n):
    max_value = 255
    interval = int(max_value / n)
    hues = range(0, max_value, interval)
    return cl.to_rgb(["hsl(%d,100%%,40%%)"%i for i in hues])

class MatrixPlotter:
    def __init__(self, DS, mode="notebook", base_path = None):
        self.DS = DS
        self.plot_mode = mode
        self.base_path = base_path

    def makeplot(self, fig, local_path=None):
        """Make the plotly figure visable to the user in the way they want.

        Parameters
        ----------
        gid : :obj:`figure`
            An plotly figure.

        """

        if self.plot_mode == "notebook":
            iplot(fig)
        if self.plot_mode == "savediv":
            fig["layout"]["autosize"] = True
            div = plot(fig, output_type='div', include_plotlyjs=False)
            path = os.path.join(self.base_path, local_path + ".html")
            os.makedirs("/".join(path.split("/")[:-1]), exist_ok=True)
            with open(path, "w") as f:
                f.write(div)
                f.close()

        if self.plot_mode == "div":
            fig["layout"]["autosize"] = True
            return plot(fig, output_type='div', include_plotlyjs=False)

class TimeSeriesPlotter:
    """A generic one-to-one plotter for time series data to be extended.

    Parameters
    ----------
    data : :obj:`ndarray`
        The time series data.
    resource_name : string
        The name of the time series being plotted.
    row_name : string
        The name of the rows in the time-series (e.g. channels, sources. ect.).
    column_name : string
        The name of the columns in the time-series (e.g. time points, time steps, seconds, ect.).

    Attributes
    ----------
    data : :obj:`ndarray`
        The time series data.
    d : int
        The number of dimensions in the time series
    n : int
        The number of time points in the time series
    row_name : string
        The name of the rows in the time-series (e.g. channels, sources. ect.).
    column_name : string
        The name of the columns in the time-series (e.g. time points, time steps, seconds, ect.).
    resource_name : string
        The name of the time series being plotted.

    """

    def __init__(self, DS, mode = "notebook", base_path=None):
        self.data = DS.D.as_matrix().T
        self.d, self.n = self.data.shape
        self.row_name = "Channels"
        self.col_name = "Time Points"
        self.resource_name = DS.name
        self.plot_mode = mode
        self.base_path = base_path

    def makeplot(self, fig, local_path=None):
        """Make the plotly figure visable to the user in the way they want.

        Parameters
        ----------
        gid : :obj:`figure`
            An plotly figure.

        """

        if self.plot_mode == "notebook":
            iplot(fig)
        if self.plot_mode == "savediv":
            fig["layout"]["autosize"] = True
            div = plot(fig, output_type='div', include_plotlyjs=False)
            path = os.path.join(self.base_path, local_path + ".html")
            os.makedirs("/".join(path.split("/")[:-1]), exist_ok=True)
            with open(path, "w") as f:
                f.write(div)
                f.close()

        if self.plot_mode == "div":
            fig["layout"]["autosize"] = True
            return plot(fig, output_type='div', include_plotlyjs=False)


class GraphPlotter:
    """
    Visualization of summary statistics of a list of graphs

    Parameters
    ----------
    fs : list
        List of strings of filenames of graphs to be analyzed
    outf: string
        name of plotly html output file
    """
    def __init__(self, fs, outf):

        self.file_list = fs
        self.outf = outf

    def makeplot(self, modality='dwi', atlas = None, log = True):

        statsDict = qg.compute_metrics(fs, modality)
        qpg.make_panel_plot(statsDict, outf, atlas, log, modality)


class SquareHeatmap(MatrixPlotter):
    titlestring = "%s Heatmap"
    shortname = "squareheat"

    def plot(self):
        """Constructs a distance matrix heatmap using the :obj:`DistanceMatrix` object, in plotly.

        """
        title = self.titlestring % (self.DS.name)
        xaxis = go.XAxis(
                title=self.DS.D.index.name,
                ticktext = self.DS.D.index,
                ticks = "",
                showticklabels=False,
                showgrid=False,
                mirror=True,
                tickvals = [i for i in range(len(self.DS.D.index))])
        yaxis = go.YAxis(
                scaleanchor="x",
                title=self.DS.D.index.name,
                ticktext = self.DS.D.index,
                showgrid=False,
                ticks = "",
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(len(self.DS.D.index))])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = self.DS.D.as_matrix().T)
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class Scatterplot(MatrixPlotter):
    titlestring = "%s Scatterplot"
    shortname = "scatter"

    def plot(self):
        """Constructs a distance matrix heatmap using the :obj:`DistanceMatrix` object, in plotly.

        """
        title = self.titlestring % (self.DS.name)
        if self.DS.d != 2:
            print("Scatter plot must get 2 dimensional dataset")
            return
        xaxis = go.XAxis(title=self.DS.D.index.name)
        yaxis = go.YAxis(scaleanchor="x", title=self.DS.D.index.name)
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Scatter(x = self.DS.D.as_matrix()[:, 0],
                           y = self.DS.D.as_matrix()[:, 1],
                           mode = "markers")
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class ThreeDScatterplot(MatrixPlotter):
    titlestring = "%s 3D Scatter Plot"
    shortname = "3sp"

    def plot(self):
        title = self.titlestring % (self.DS.name)

        if self.DS.d < 3:
            print("Scatter plot must get at least 3 dimensional dataset")
            return
        xaxis = go.XAxis(title=list(self.DS.D)[0])
        yaxis = go.YAxis(title=list(self.DS.D)[1])
        zaxis = go.ZAxis(title=list(self.DS.D)[2])
        layout = dict(title=title, scene=dict(
            xaxis=xaxis,
            yaxis=yaxis,
            zaxis=zaxis
        ))
        trace = go.Scatter3d(
            x=self.DS.D.as_matrix()[:, 0],
            y=self.DS.D.as_matrix()[:, 1],
            z=self.DS.D.as_matrix()[:, 2],
            mode='markers',
            marker=dict(
                size=4
            )
        )
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class SpatialConnectivity(MatrixPlotter):
    titlestring = "%s Spatial Connectivity"
    shortname = "spatialconn"

    def plot(self, spatial):
        title = self.titlestring % (self.DS.name)
        DM = self.DS.D.as_matrix()
        sp = spatial.D.as_matrix()
        trace1 = go.Scatter3d(
            x=sp[:, 0],
            y=sp[:, 1],
            z=sp[:, 2],
            mode='markers',
            marker=dict(
                size=12,
                opacity=0
            )
        )
        #med = np.nanmedian(DM)
        #mask = np.nan_to_num(DM) > (3 * med)
        #Xe = []
        #Ye = []
        #Ze = []
        #for i in range(DM.shape[0]):
        #    for j in range(DM.shape[1]):
        #        if mask[i, j]:
        #            Xe += [sp[i, 0], sp[j, 0], None]
        #            Ye += [sp[i, 1], sp[j, 1], None]
        #            Ze += [sp[i, 2], sp[j, 2], None]
        #print(Xe)
        #trace2 = go.Scatter3d(x=Xe,
        #                      y=Ye,
        #                      z=Ze,
        #                      mode='lines',
        #                      line=go.Line(color='rgb(125,125,125)', width=1),
        #                      hoverinfo='none')
        data = [trace1]
        fig = dict(data=data, layout={"autosize":True})
        return self.makeplot(fig, self.DS.name + "/" + self.shortname)

class ConnectedScatterplot(MatrixPlotter):
    titlestring = "%s Scatterplot"
    shortname = "connectedscatter"

    def plot(self, spatialDM):
        """Constructs a distance matrix heatmap using the :obj:`DistanceMatrix` object, in plotly.

        """
        title = self.titlestring % (self.DS.name)
        DM = self.DS.D.as_matrix()
        sDM = spatialDM.D.as_matrix()
        colors = (np.nansum(DM, axis=0) - 1) / DM.shape[0]
        TSNEEmbedder = leb.TSNEEmbedder(num_components=2)
        m = TSNEEmbedder.embed(sDM)
        xaxis = go.XAxis(title=spatialDM.D.index.name)
        yaxis = go.YAxis(scaleanchor="x", title=spatialDM.D.index.name)
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis, showlegend=False)
        trace1 = go.Scatter(x = m[:, 0],
                           y = m[:, 1],
                           mode = "markers",
                           marker = dict(color=colors, size=16, showscale=True))
        distances = np.zeros([m.shape[0], m.shape[0]])
        for i in range(m.shape[0]):
            for j in range(m.shape[0]):
                distances[i, j] = np.linalg.norm(m[i, :] - m[j, :])
        med = np.median(distances)
        mask = distances < (med / 4)
        Xe = []
        Ye = []
        for i in range(distances.shape[0]):
            for j in range(distances.shape[1]):
                if mask[i, j]:
                    Xe += [m[i, 0], m[j, 0], None]
                    Ye += [m[i, 1], m[j, 1], None]
        trace2 = go.Scatter(x=Xe,
                            y=Ye,
                            mode='lines',
                            line=go.Line(color='rgb(125,125,125)', width=1),
                            hoverinfo='none')
        data = [trace1, trace2]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, self.DS.name + "/" + self.shortname)

class Scatterplot(MatrixPlotter):
    titlestring = "%s Scatterplot"
    shortname = "scatter"

    def plot(self):
        """Constructs a distance matrix heatmap using the :obj:`DistanceMatrix` object, in plotly.

        """
        title = self.titlestring % (self.DS.name)
        if self.DS.d != 2:
            print("Scatter plot must get 2 dimensional dataset")
            return
        xaxis = go.XAxis(title=self.DS.D.index.name)
        yaxis = go.YAxis(scaleanchor="x", title=self.DS.D.index.name)
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Scatter(x = self.DS.D.as_matrix()[:, 0],
                           y = self.DS.D.as_matrix()[:, 1],
                           mode = "markers")
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class Heatmap(MatrixPlotter):
    titlestring = "%s Heatmap"
    shortname = "heatmap"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        xaxis = go.XAxis(
                title="observaions",
                ticktext = self.DS.D.index,
                showticklabels=False,
                tickvals = [i for i in range(len(self.DS.D.index))])
        yaxis = go.YAxis(
                title="dimensions",
                ticktext = self.DS.D.columns,
                showticklabels=False,
                tickvals = [i for i in range(len(self.DS.D.columns))])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = self.DS.D.as_matrix().T)
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class LocationHeatmap(MatrixPlotter):
    titlestring = "%s Location Heatmap"
    shortname = "locationheat"

    def plot(self, showticklabels=False):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        means = np.mean(D, axis=1)
        medians = np.median(D, axis=1)
        z = np.vstack([means, medians])
        yaxis = go.YAxis(
                ticktext = ["mean", "median"],
                showticklabels=True,
                tickvals = [0, 1])
        xaxis = go.XAxis(
                title="dimensions",
                showticklabels=showticklabels)
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(x = self.DS.D.columns,
                           z = z)
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class LocationLines(MatrixPlotter):
    titlestring = "%s Embedding Location Lines"
    shortname = "locationlines"

    def plot(self, showticklabels=False):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        means = np.mean(D, axis=1)
        medians = np.median(D, axis=1)
        trace0 = go.Scatter(x = self.DS.D.columns,
                            y = means,
                            name="means")
        trace1 = go.Scatter(x = self.DS.D.columns,
                            y = medians,
                            name="medians")
        layout = dict(title=title,
                      xaxis=dict(title="Dimensions",
                                 showticklabels=showticklabels),
                      yaxis=dict(title="Mean or Median Value"))
        data = [trace0, trace1]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class HistogramHeatmap(MatrixPlotter):
    titlestring = "%s Histogram Heatmap"
    shortname = "histogramheat"

    def plot(self, showticklabels=False):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        d, n = D.shape
        D = (D - np.mean(D, axis=1).reshape(d, 1)) / np.std(D, axis=1).reshape(d, 1)
        D = np.nan_to_num(D) # only nan if std all 0 -> all values 0
        num_bins = int(np.sqrt(n))
        bins = np.linspace(-5, 5, num_bins + 1)
        bin_centers = (bins[1:] + bins[:-1]) / 2
        H = []
        for i in range(D.shape[0]):
            hist = np.histogram(D[i, :], bins = bins)[0]
            H.append(hist)
        z = np.vstack(H)
        trace = go.Heatmap(y = self.DS.D.columns,
                           z = z)
        data = [trace]
        xaxis = go.XAxis(
                title="Normalized Value",
                ticktext = list(map(lambda x: "%0.4f"%x, bin_centers)),
                ticks = "",
                showticklabels=True,
                mirror=True,
                tickvals = [i for i in range(len(bin_centers))])
        yaxis = go.YAxis(
                title="Dimensions",
                ticks = "",
                showticklabels=showticklabels,
                mirror=True)
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        fig = dict(data = data, layout = layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class CorrelationMatrix(MatrixPlotter):
    titlestring = "%s Correlation Matrix"
    shortname = "correlation"

    def plot(self, showticklabels=False):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        xaxis = dict(
            title = "Dimensions",
            ticks = "",
            showgrid=False,
            zeroline=False,
            showticklabels=showticklabels,
        )
        yaxis = dict(
            scaleanchor="x",
            title = "Dimensions",
            ticks = "",
            showgrid=False,
            zeroline=False,
            showticklabels=showticklabels,
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            C = np.nan_to_num(np.corrcoef(D))

        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(x = self.DS.D.columns,
                           y = self.DS.D.columns,
                           z = C,
                           zmin = -1,
                           zmax = 1)
        fig = dict(data=[trace], layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class ScreePlotter(MatrixPlotter):
    titlestring = "%s Scree Plot"
    shortname = "scree"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        _, S, _ = np.linalg.svd(D, full_matrices=False)
        y = S
        x = np.arange(1, len(S) + 1)
        sy = np.sum(y)
        cy = np.cumsum(y)
        xaxis = dict(
            title = 'Factors'
        )
        yaxis = dict(
            title = 'Proportion of Total Variance'
        )
        var = go.Scatter(mode = 'lines+markers',
                         x = x,
                         y = y / sy,
                         name = "Variance")
        cumvar = go.Scatter(mode = 'lines+markers',
                            x = x,
                            y = cy / sy,
                            name = "Cumulative Variance")
        data = [var, cumvar]
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class EigenvectorHeatmap(MatrixPlotter):
    titlestring = "%s Eigenvector Heatmap"
    shortname = "evheat"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        d, n = D.shape
        U, _, _ = np.linalg.svd(D, full_matrices=False)
        xaxis = go.XAxis(
                title="Eigenvectors",
                ticktext = ["Eigenvector %s"%i for i in range(1, d + 1)],
                ticks = "",
                showgrid=False,
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(d)])
        yaxis = go.YAxis(
                title="Eigenvector Components",
                scaleanchor="x",
                showgrid=False,
                ticktext = ["Component %s"%i for i in range(1, d + 1)],
                ticks = "",
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(d)])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = U)
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)

class HierarchicalClusterMeansDendrogram(MatrixPlotter):

    titlestring = "%s %s Cluster Means Dendrogram, Level %d"
    shortname = "cmd"

    def plot(self):
        title = self.titlestring % (self.DS.name, self.DS.clustname, self.DS.levels)
        self.shortname = self.DS.shortclustname + self.shortname
        means = []
        for c in self.DS.clusters[self.DS.levels]:
            means.append(np.average(c, axis=0))
        X = np.column_stack(means).T
        fig = ff.create_dendrogram(X)
        fig["layout"]["title"] = title
        fig["layout"]["xaxis"]["title"] = "Cluster Labels"
        fig["layout"]["yaxis"]["title"] = "Cluster Mean Distances"
        del fig.layout["width"]
        del fig.layout["height"]
        return self.makeplot(fig, "agg/" + self.shortname)


class HierarchicalStackedClusterMeansHeatmap(MatrixPlotter):
    titlestring = "%s %s Stacked Cluster Means, Level %d"
    shortname = "scmh"

    def plot(self, showticklabels=False):
        title = self.titlestring % (self.DS.name, self.DS.clustname, self.DS.levels)
        self.shortname = self.DS.shortclustname + self.shortname

        Xs = []
        for l in self.DS.clusters[1:self.DS.levels + 1]:
            #When number of samples is too high, need to downsample
            freq = [c.shape[0] for c in l]
            if sum(freq) > 500:
                freq = [round((x / sum(freq)) * 500) for x in freq]
                if sum(freq) != 500: #Rounding can give numbers not exactly 500
                    freq[freq.index(max(freq))] += (500 - sum(freq))

            means = []
            for i, c in enumerate(l):
                means += [np.average(c, axis=0)] * freq[i]

            X = np.column_stack(means)
            Xs.append(X)
        X = np.vstack(Xs)[::-1, :]
        y_labels = np.tile(self.DS.columns, X.shape[0] // len(self.DS.columns))[::-1]
        trace = go.Heatmap(z = X,
                           zmin = -np.max(X),
                           zmax = np.max(X))
        data = [trace]
        xaxis = go.XAxis(
                title="Clusters",
                showticklabels=False,
                ticks="",
                mirror=True,
                tickvals = [i for i in range(X.shape[1])])
        yaxis = go.YAxis(
                title="Dimensions",
                showticklabels=showticklabels,
                ticks="",
                ticktext = y_labels,
                tickvals = [i for i in range(len(y_labels))],
                mirror=True)
        emb_size = len(np.average(self.DS.clusters[0][0], axis=0))
        bar_locations = np.arange(0, X.shape[0]  + emb_size - 1, emb_size) - 0.5
        shapes = [dict(type="line",x0=-0.5, x1=X.shape[1] - 0.5, y0=b, y1=b) for b in bar_locations]
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis, shapes=shapes)
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)


class ClusterMeansLevelHeatmap(MatrixPlotter):
    titlestring = "%s %s Cluster Means, Level %d"
    shortname = "cmlh"

    def plot(self, showticklabels=False):
        title = self.titlestring % (self.DS.name, self.DS.clustname, self.DS.levels)
        self.shortname = self.DS.shortclustname + self.shortname

        #When number of samples is too high, need to downsample
        freq = [c.shape[0] for c in self.DS.clusters[self.DS.levels]]
        if sum(freq) > 500:
            freq = [round((x / sum(freq)) * 500) for x in freq]

        means = []
        for i, c in enumerate(self.DS.clusters[self.DS.levels]):
            means += [np.average(c, axis=0)] * freq[i]
        X = np.column_stack(means)

        trace = go.Heatmap(y = self.DS.columns,
                           z = X)
        data = [trace]
        xaxis = go.XAxis(
                title="Clusters",
                showticklabels=False,
                ticks="",
                mirror=True,
                tickvals = [i for i in range(X.shape[1])])
        yaxis = go.YAxis(
                title="Dimensions",
                showticklabels=showticklabels,
                ticks="",
                mirror=True)
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)


class ClusterMeansLevelLines(MatrixPlotter):
    titlestring = "%s %s Cluster Means, Level %d"
    shortname = "cmll"

    def plot(self, showticklabels=False):
        title = self.titlestring % (self.DS.name, self.DS.clustname, self.DS.levels)
        self.shortname = self.DS.shortclustname + self.shortname
        data = []
        colors = get_spaced_colors(len(self.DS.clusters[self.DS.levels]))

        #When number of samples is too high, need to downsample
        freq = [c.shape[0] for c in self.DS.clusters[self.DS.levels]]
        if sum(freq) > 300:
            freq = [round((x / sum(freq)) * 300) for x in freq]

        for i, c in enumerate(self.DS.clusters[self.DS.levels]):
            data.append(go.Scatter(x = np.average(c, axis=0),
                                   y = self.DS.columns,
                                   mode="lines",
                                   line=dict(width=np.sqrt(freq[i]), color=colors[i]),
                                   name="cluster " + str(i)))
        xaxis = go.XAxis(
                title="Mean Values",
                showticklabels=False,
                mirror=True)
        yaxis = go.YAxis(
                title="Dimensions",
                showticklabels=showticklabels,
                mirror=True)
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, "agg/" + self.shortname)


class ClusterPairsPlot(MatrixPlotter):
    titlestring = "%s %s Classification Pairs Plot, Level %d"
    shortname = "cpp"

    def plot(self):
        title = self.titlestring % (self.DS.name, self.DS.clustname, self.DS.levels)
        self.shortname = self.DS.shortclustname + self.shortname
        data = []
        colors = get_spaced_colors(len(self.DS.clusters[self.DS.levels]))
        samples = []
        labels = []
        for i, c in enumerate(self.DS.clusters[self.DS.levels]):
            samples.append(c.T)
            labels.append(c.shape[0] * [i])
        samples = np.hstack(samples)[:3, :]
        labels = np.hstack(labels)
        df = pd.DataFrame(samples.T, columns=["Dim %d"%i for i in range(samples.shape[0])])
        df["label"] = ["Cluster %d"%i for i in labels]
        fig = ff.create_scatterplotmatrix(df, diag='box', index="label", colormap=colors)
        fig["layout"]["title"] = title
        del fig.layout["width"]
        del fig.layout["height"]
        return self.makeplot(fig, "agg/" + self.shortname)


class DistanceMatrixPlotter:
    """A generic aggregate plotter acting on a distance matrix to be extended.

    Parameters
    ----------
    dm : :obj:`DistanceMatrix`
        The distance matrix object.
    primary_label : string
        The name of the column of the dataset which contains the primary label. By default, this is the `resource_path` column which is just the path to the data point resource.
    Attributes
    ----------
    dataset_name : string
        The name of the dataset from which this distance matrix was computed.
    dm : :obj:`ndarray`
        The distance matrix.
    label_name : string
        The name of the primary label to be conditioned on in some plots.
    label : :obj:`list`
        A list of labels (the primary label) for each data point.
    metric_name : string
        The name of the metric which with the distance matrix was computed.

    """

    def __init__(self, dm, mode = "notebook", primary_label = "resource_path"):
        self.dataset_name = dm.dataset.name
        self.dm = dm.getMatrix()
        self.labels = dm.labels
        self.label_name = dm.label_name
        self.metric_name = dm.metric.__name__
        self.plot_mode = mode

    def makeplot(self, fig):
        """Make the plotly figure visable to the user in the way they want.

        Parameters
        ----------
        gid : :obj:`figure`
            An plotly figure.

        """

        if self.plot_mode == "notebook":
            iplot(fig)
        if self.plot_mode == "html":
            fig["layout"]["autosize"] = True
            h = random.getrandbits(128)
            fname = "%032x.html"%h
            plot(fig, output_type='file', filename=fname)

class CSVPlotter:
    def __init__(self, ds, mode = "notebook"):
        self.ds = ds
        self.plot_mode = mode

    def makeplot(self, fig):
        """Make the plotly figure visable to the user in the way they want.

        Parameters
        ----------
        gid : :obj:`figure`
            An plotly figure.

        """

        if self.plot_mode == "notebook":
            iplot(fig)
        if self.plot_mode == "html":
            fig["layout"]["autosize"] = True
            h = random.getrandbits(128)
            fname = "%032x.html"%h
            plot(fig, output_type='file', filename=fname)
        if self.plot_mode == "div":
            fig["layout"]["autosize"] = True
            return plot(fig, output_type='div', include_plotlyjs=False)


class ColumnDistributionPlotter(CSVPlotter):
    def plot(self, column):
        x, y = self.ds.getColumnDistribution(column)
        yn = y / np.nansum(y)
        # title = "Column Distribution Plot<br>" + self.ds.getColumnDescription(column, sep="<br>")
        title = "Column Distribution Plot<br>"
        trace_frequency = go.Bar(
            x = x,
            y = y,
            name = 'Frequency'
        )
        trace_proportion = go.Bar(
            x = x,
            y = yn,
            visible = False,
            name = 'Proportion'
        )
        layout = go.Layout(
            title = title,
            xaxis = dict(title="Value"),
            yaxis = dict(title="Frequency")
        )
        updatemenus = list([
            dict(buttons = list([
                dict(args = [{'visible': [True, False]}, {'yaxis': dict(title="Frequency")}],
                     label = 'Frequency',
                     method = 'update'
                ),
                dict(args = [{'visible': [False, True]}, {'yaxis': dict(title="Proportion")}],
                     label = 'Proportion',
                     method = 'update'
                ),
                ]),
                showactive = True,
                type = 'buttons'
            )
        ])
        layout.updatemenus = updatemenus
        fig = go.Figure(data = [trace_frequency, trace_proportion], layout=layout)
        return self.makeplot(fig)

class ColumnNADistPlotter(CSVPlotter):
    def plot(self, column):
        na, not_na = self.ds.getColumnNADist(column)
        title = "Column NA Distribution Plot<br>" + self.ds.getColumnDescription(column, sep="<br>")
        trace = go.Pie(
            labels = ['NA', 'Not NA'],
            values = [na, not_na]
        )
        layout = go.Layout(
            title=title
        )
        fig = go.Figure(data = [trace], layout=layout)
        return self.makeplot(fig)

class EverythingPlotter(CSVPlotter):
    html_data = """
	<html>
	    <head>
		<title>
		%s
		</title>
		<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
	    </head>
	    <body>
              %s
            </body>
         </html>
	"""
    def plot(self, base, plotter):
        cp = plotter(self.ds, mode="div")
        for c in self.ds.D.columns:
            path = os.path.join(base, *c)
            os.makedirs(path, exist_ok=True)
            div = cp.plot(c)
            with open(os.path.join(path, plotter.__name__ + ".html"), "w") as f:
                f.write(self.html_data%(plotter.__name__, div))

class EmbeddingParallelCoordinatePlotter(DistanceMatrixPlotter):
    titlestring = "%s-%s-Embedding-Parallel-Coordinate-Plot-under-%s-metric"

    def plot(self, embedder):
        """Constructs a parallel coordinate plot of the embedded :obj:`DistanceMatrix` object.

        Parameters
        ----------
        embedder : :obj:`BaseEmbedder`


        """
        title = self.titlestring % (self.dataset_name, embedder.embedding_name, self.metric_name)
        emb = embedder.embed(self.dm)
        D = emb.T
        d, n = D.shape
        D = D - np.min(D, axis=1).reshape(d, 1)
        D = D / np.max(D, axis=1).reshape(d, 1)
        unique_labels = np.unique(self.labels)
        label_to_number = dict(zip(unique_labels, range(1, len(unique_labels) + 1)))
        dims = [dict(label = "factor %s"%(x + 1),
                values = D[x, :]) for x in range(embedder.num_components)]
        line = dict(color = [label_to_number[x] for x in self.labels],
                    cmin = 0,
                    cmax = len(unique_labels),
                    colorscale = "Jet",
                    showscale=True,
                    colorbar = dict(tickmode = "array",
                                    ticktext = unique_labels,
                                    tickvals = [label_to_number[x] for x in unique_labels]))
        trace = go.Parcoords(line = line, dimensions = list(dims))
        data = [trace]
        layout = go.Layout(
            title=title
        )
        fig = dict(data = data, layout = layout)
        self.makeplot(fig)




class SparkLinePlotter(TimeSeriesPlotter):
    titlestring = "Sparklines for %s"
    shortname = "sparkline"

    def plot(self, sample_freq):
        """Constructs a downsampled spark line plot of the time series.

        If there are more than 500 time points, the time series will be down sampled to
        500 column variables by windowed averaging. This is done by splitting the time series
        into 500 equal sized segments in the time domain, then plotting the mean for each segment.

        Parameters
        ----------
        sample_freq : int
            The sampling frequency (how many times sampled per second).

        """
        title = self.titlestring % (self.resource_name)
        xaxis = dict(
            title = "Time in Seconds"
        )
        yaxis = dict(
            title = "Intensity"
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        if self.n > 500:
            winsize = self.n // 500
            df = pd.DataFrame(self.data.T)
            df = df.groupby(lambda x: x // winsize).mean()
            downsampled_data = df.as_matrix().T
            data = [dict(mode="lines",
                         name = str(i),
                         x=(np.arange(downsampled_data.shape[1]) * winsize) / sample_freq,
                         y=downsampled_data[i, :]) for i in range(downsampled_data.shape[0])]
        fig = dict(data=data, layout=layout)
        self.makeplot(fig, self.resource_name + "/" + self.shortname)

class CorrelationMatrixPlotter(TimeSeriesPlotter):
    titlestring = "Correlation Matrix for %s"

    def plot(self):
        title = self.titlestring % (self.resource_name)
        xaxis = dict(
            title = "Channels"
        )
        yaxis = dict(
                scaleanchor="x",
            title = "Channels"
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            C = np.nan_to_num(np.corrcoef(self.data))

        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = C)
        fig = dict(data=[trace], layout=layout)
        self.makeplot(fig)

class CoherenceMatrixPlotter(TimeSeriesPlotter):
    titlestring = "Coherence Matrix for %s"

    def plot(self, samp_freq = 500):
        title = self.titlestring % (self.resource_name)
        xaxis = dict(
            title = "Channels"
        )
        yaxis = dict(
                scaleanchor="x",
            title = "Channels"
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        C = np.zeros([self.d, self.d])
        for i in range(self.d):
            for j in range(i + 1):
                C[i, j] = np.mean(np.nan_to_num(signal.coherence(self.data[i, :],
                                                              self.data[j, :],
                                                              fs=samp_freq)[1]))
                C[j, i] = C[i, j]

        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = C)
        fig = dict(data=[trace], layout=layout)
        self.makeplot(fig)

class SpectrogramPlotter(TimeSeriesPlotter):
    titlestring = "Spectrograms for %s"

    def plot(self, channel = 0, sample_freq = 500):
        """Constructs a spectrogram plot of the time series.

        Parameters
        ----------
        sample_freq : int
            The sampling frequency (how many times sampled per second).

        """
        title = self.titlestring % (self.resource_name)
        xaxis = dict(
            title = "Hz",
            range = [0, 10]
        )
        yaxis = dict(
            title = "Intensity",
            range = [0, 1000]
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)

        dt = 1./sample_freq
        sample_points = np.arange(self.data.T.shape[1]) * dt
        signal = self.data.T[channel, :]
        ft = np.fft.fft(signal) * dt
        ft = ft[: len(sample_points)//2]
        freq = np.fft.fftfreq(len(sample_points), dt)
        freq = freq[:len(sample_points)//2]

        trace = go.Scatter(
            x = freq[:2000],
            y = np.abs(ft)[:2000],
            mode = 'markers'
        )

        fig= dict(data=[trace], layout=layout)
        iplot(fig)

class SpatialTimeSeries(TimeSeriesPlotter):
    titlestring = "Intensity by Time and Channel Location for %s"
    shortname = "spatialtimeseries"

    def plot(self, spatial, downsample = 1000):
        """Constructs a plot of the channel locations, and their intensities at different times.

        Parameters
        ----------
        spatial : Dataset
            Locations of channels.

        """
        title = self.titlestring % (self.resource_name)
        # Time series containing EEG data.
        mts = self.data.T

        # Set variables
        num_obs = mts.shape[0]
        num_channels = mts.shape[1]

        # Verify that 'locations' exist for exactly each channel.
        if (num_channels != spatial.shape[0]):
            raise TypeError("""Error: Ensure that the number of channels in the Multivariate Time Series (columns)
                            is equal to the number of points (rows) in locations.""")

        # Sets up data frame containing the different plots.
        data = [go.Scatter3d(dict(
            visible = False,
            name = str(step),
            x = spatial[:, 0],
            y = spatial[:, 1],
            z = spatial[:, 2],
            mode = 'markers',
            # Marker represents intensity.
            marker = dict(
            size = 8,
            color = mts[step, range(num_channels)],
            colorbar = go.ColorBar(
                    title='Voltage'
                ),
            colorscale='Viridis',
            line = dict(
                width = 1,
                color = 'rgb(0, 0, 0)'
            )))) for step in range(0, num_obs, downsample)]

        # Set up timesteps
        steps = []
        for i in range(len(data)):
            step = dict(
                method = 'restyle',
                args = ['visible', [False] * len(data)],
            )
            step['args'][1][i] = True # Toggle i'th trace to "visible"
            steps.append(step)

        # Sets up slider
        sliders = [dict(
            active = 10,
            currentvalue = {"prefix": "Timestep: "},
            pad = {"t": 50},
            steps = steps
        )]
        layout = dict(sliders=sliders)

        # Plot figure.
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, self.resource_name + "/" + self.shortname)

class SpatialPeriodogram(TimeSeriesPlotter):
    titlestring = "Density by Frequency and Channel Location for %s"
    shortname = "spatialpgram"

    def plot(self, spatial, downsample = 1000):
        """Constructs a plot of the channel locations, and their densities at different frequencies.

        Parameters
        ----------
        spatial : Dataset
            Locations of channels.

        """
        title = self.titlestring % (self.resource_name)
        # Time series containing EEG data.
        mts = self.data.T

        # Set variables
        num_obs = mts.shape[0]
        num_channels = mts.shape[1]

        # Create matriz to hold frequencies and densities
        freq0, density0 = signal.periodogram(mts[0:num_obs:downsample,0])
        densities = np.zeros((len(density0), num_channels))
        densities[:, 0] = density0
        for j in range(1, num_channels):
            freq, density = signal.periodogram(mts[0:num_obs:downsample,j])
            densities[:, j] = density
        num_dens = densities.shape[0]

        # Verify that 'locations' exist for exactly each channel.
        if (num_channels != spatial.shape[0]):
            raise TypeError("""Error: Ensure that the number of channels in the Multivariate Time Series (columns)
                            is equal to the number of points (rows) in locations.""")

        # Sets up data frame containing the different plots.
        data = [go.Scatter3d(dict(
            visible = False,
            name = 'Frequency = '+str(step),
            x = spatial[:, 0],
            y = spatial[:, 1],
            z = spatial[:, 2],
            mode = 'markers',
            # Marker represents density.
            marker = dict(
            size = 8,
            color = densities[step, range(num_channels)],
            colorbar = go.ColorBar(
                    title='Power Density'
                ),
            colorscale='Viridis',
            line = dict(
                width = 1,
                color = 'rgb(0, 0, 0)'
            )))) for step in range(num_dens)]

        # Set up timesteps
        steps = []
        for i in range(len(data)):
            step = dict(
                method = 'restyle',
                args = ['visible', [False] * len(data)],
            )
            step['args'][1][i] = True # Toggle i'th trace to "visible"
            steps.append(step)

        # Sets up slider
        sliders = [dict(
            active = 10,
            currentvalue = {"prefix": "Frequency: "},
            pad = {"t": 50},
            steps = steps
        )]
        layout = dict(sliders=sliders)

        # Plot figure.
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig, self.resource_name + "/" + self.shortname)

class Nifti4DPlotter:
    name = "Nifti4DPlotter"
    def __init__(self, resource):
        self.path = resource[0]
        self.subject = resource[1]
        self.task = resource[2]

    def plot(self, downsample=1, out_base="."):
        out_path = os.path.join(out_base, self.subject, self.name, self.task)
        os.makedirs(out_path, exist_ok=True)
        raw = nib.load(self.path)
        M = np.max(raw.get_data())
        n = raw.shape[3]
        mean = nimage.mean_img(raw)
        xyzcuts = nilplot.find_xyz_cut_coords(mean)
        xcuts = nilplot.find_cut_slices(mean, "x")
        ycuts = nilplot.find_cut_slices(mean, "y")
        zcuts = nilplot.find_cut_slices(mean, "z")
        del raw
        nrange = range(0, n, downsample)
        for i, img in enumerate(nimage.iter_img(self.path)):
            if i in nrange:
                nilplot.plot_epi(nimage.math_img("img / %f"%(M), img=img),
                                  colorbar=False,
                                  output_file="%s/orth_epi%0d.png"%(out_path, i),
                                  annotate=True,
                                  cut_coords = xyzcuts,
                                  cmap="gist_heat")
                nilplot.plot_epi(nimage.math_img("img / %f"%(M), img=img),
                                  colorbar=False,
                                  output_file="%s/x_epi%0d.png"%(out_path, i),
                                  annotate=True,
                                  display_mode = "x",
                                  cut_coords = xcuts,
                                  cmap="gist_heat")
                nilplot.plot_epi(nimage.math_img("img / %f"%(M), img=img),
                                  colorbar=False,
                                  output_file="%s/y_epi%0d.png"%(out_path, i),
                                  annotate=True,
                                  display_mode = "y",
                                  cut_coords = ycuts,
                                  cmap="gist_heat")
                nilplot.plot_epi(nimage.math_img("img / %f"%(M), img=img),
                                  colorbar=False,
                                  output_file="%s/z_epi%0d.png"%(out_path, i),
                                  annotate=True,
                                  display_mode = "z",
                                  cut_coords = zcuts,
                                  cmap="gist_heat")


        slice_names = ["orth_epi", "x_epi", "y_epi", "z_epi"]
        for slic in slice_names:
            filenames = ["%s/%s%0d.png"%(out_path, slic, i) for i in nrange]
            with imageio.get_writer('%s/%s.gif'%(out_path, slic), mode='I') as writer:
                for i, filename in zip(nrange, filenames):
                    image = Image.open(filename)
                    draw = ImageDraw.Draw(image)
                    fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 16)
                    draw.text((2, 2), str(i), font=fnt, fill=(255, 0, 0, 255))
                    image.save(filename, "PNG")
                    image = imageio.imread(filename)
                    writer.append_data(image)
