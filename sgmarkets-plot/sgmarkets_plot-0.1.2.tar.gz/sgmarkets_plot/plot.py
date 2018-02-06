
import os
import json

import datetime as dt
import numpy as np
import pandas as pd

import matplotlib.pyplot as pl
import seaborn as sns
import ezhc as hc
import ezvis3d as v3d

from IPython.display import display

from ._util import Util

from .sg_color import SG_COLORS_MATPLOTLIB, SG_THEME_HIGHCHARTS, \
    CMAP_SG_BuRd, CMAP_SG_RdBu


class Plot:

    @staticmethod
    def line(df,
             save=False,
             folder_save='dump',
             name=None,
             tagged=True,
             cmap=None,
             **kwargs):
        """
        """
        with sns.axes_style("darkgrid"):
            if not cmap:
                kwargs['color'] = SG_COLORS_MATPLOTLIB
            else:
                kwargs['cmap'] = cmap

            ax = df.plot(**kwargs)
            ax.legend(bbox_to_anchor=(1.1, 1.0),
                      loc='upper center')
            if df.columns.name:
                ax.set_ylabel(df.columns.name)

            # plot
            pl.show()

            if save:
                # prepare save
                if not os.path.exists(folder_save):
                    os.makedirs(folder_save)
                if not name:
                    name = 'plot'
                tag = ''
                if tagged:
                    tag = dt.datetime.now().strftime('_%Y%m%d_%H%M%S')
                suffix = '.png'
                filename = '{}{}{}'.format(name, tag, suffix)
                path = os.path.join(folder_save, filename)

                fig = ax.get_figure()
                fig.savefig(path)

    @staticmethod
    def heatmap(df,
                save=False,
                folder_save='dump',
                name=None,
                tagged=True,
                figsize=(9, 9),
                title=None,
                cmap=None,
                **kwargs):
        """
        """

        sns.set(font_scale=1.2)
        sns.set_style({'savefig.dpi': 100})

        # plot it out
        if cmap is not None:
            if cmap == 'SG-BuRd':
                cmap = CMAP_SG_BuRd
            elif cmap == 'SG-RdBu':
                cmap = CMAP_SG_RdBu
            else:
                cmap = getattr(pl.cm, cmap)
        else:
            # cmap = pl.cm.RdBu
            cmap = sns.diverging_palette(23, 248, s=70.4, l=40,
                                         center='light',
                                         as_cmap=True)
        ax = sns.heatmap(df,
                         cmap=cmap,
                         linewidths=.1,
                         **kwargs)

        # set the x-axis labels on the top
        # (not good as overlap with title)
        # ax.xaxis.tick_top()
        # ax.xaxis.label_position = 'top'

        # rotate the x-axis labels
        pl.xticks(rotation=90)
        # get figure (usually obtained via "fig,ax=plt.subplots()" with matplotlib)
        fig = ax.get_figure()
        # specify dimensions and save
        fig.set_size_inches(figsize[0], figsize[1])

        if title:
            ax.set_title(title)

        # plot
        pl.show()

        if save:
            # prepare save
            if not os.path.exists(folder_save):
                os.makedirs(folder_save)
            if not name:
                name = 'plot'
            tag = ''
            if tagged:
                tag = dt.datetime.now().strftime('_%Y%m%d_%H%M%S')
            suffix = '.png'
            filename = '{}{}{}'.format(name, tag, suffix)
            path = os.path.join(folder_save, filename)

            # save
            fig.savefig(path)

    @staticmethod
    def highstock(df,
                  save=False,
                  folder_save='dump',
                  name=None,
                  tagged=True,
                  title=None,
                  exporting=False):
        """
        """
        msg = 'df must be a DataFrame'
        assert isinstance(df, pd.DataFrame), msg
        msg = 'df must be 2D'
        assert not isinstance(df.index, pd.MultiIndex), msg
        assert not isinstance(df.columns, pd.MultiIndex), msg
        msg = 'df must have DatetimeIndex'
        assert isinstance(df.index, pd.DatetimeIndex), msg

        g = hc.Highstock()

        g.chart.height = 500
        g.legend.enabled = True
        g.legend.layout = 'horizontal'
        g.legend.align = 'center'
        g.legend.maxHeight = 100
        g.tooltip.enabled = True
        g.tooltip.valueDecimals = 2
        g.exporting.enabled = exporting

        g.chart.zoomType = 'xy'
        if title:
            g.title.text = title

        g.tooltip.positioner = hc.scripts.TOOLTIP_POSITIONER_CENTER_TOP

        g.xAxis.gridLineWidth = 1.0
        g.xAxis.gridLineDashStyle = 'Dot'
        g.yAxis.gridLineWidth = 1.0
        g.yAxis.gridLineDashStyle = 'Dot'

        g.credits.enabled = True
        g.credits.text = 'Source: SG Research'
        g.credits.href = 'https://analytics-api.sgmarkets.com/rotb/'

        g.series = hc.build.series(df)

        filename = None
        if save:
            # prepare save
            if not os.path.exists(folder_save):
                os.makedirs(folder_save)
            if not name:
                name = 'plot'
            tag = ''
            if tagged:
                tag = dt.datetime.now().strftime('_%Y%m%d_%H%M%S')
            suffix = '.html'
            filename = '{}{}{}'.format(name, tag, suffix)

        hc_global = hc.GlobalOptions(SG_THEME_HIGHCHARTS)
        hc_global.inject(verbose=False)

        html = g.plot(save=save,
                      save_path=folder_save,
                      save_name=filename)
        return html

    @staticmethod
    def surface3D(df,
                  z_label='z',
                  z_round=2,
                  width='800px',
                  height='600px',
                  save=False,
                  folder_save='dump',
                  name=None,
                  tagged=True):
        """
        """
        msg = 'df must be a DataFrame'
        assert isinstance(df, pd.DataFrame), msg
        msg = 'df must be 2D'
        assert not isinstance(df.index, pd.MultiIndex), msg
        assert not isinstance(df.columns, pd.MultiIndex), msg
        msg = 'dates are not supported - yet'
        assert not isinstance(df.index, pd.DatetimeIndex), msg
        assert not isinstance(df.T.index, pd.DatetimeIndex), msg

        dfi = df.copy()

        dic_x = {k: v for k, v in enumerate(dfi.index)}
        dic_x_rev = {v: k for k, v in dic_x.items()}

        dic_y = {k: v for k, v in enumerate(dfi.columns)}
        dic_y_rev = {v: k for k, v in dic_y.items()}

        values = dfi.stack().reset_index().values
        df_data = pd.DataFrame(data=values, columns=['x', 'y', 'z'])
        df_data.z = df_data.z.astype(np.float)

        str_dic_x = None
        if df_data.x.dtype.kind not in 'fi':
            df_data.x = [dic_x_rev[e] for e in df_data.x]
            str_dic_x = json.dumps(dic_x)

        str_dic_y = None
        if df_data.y.dtype.kind not in 'fi':
            df_data.y = [dic_y_rev[e] for e in df_data.y]
            str_dic_y = json.dumps(dic_y)

        g = v3d.Vis3d()
        g.width = width
        g.height = height
        g.style = 'surface'
        g.showPerspective = True
        g.showGrid = True

        g.xLabel = dfi.index.name
        g.yLabel = dfi.columns.name
        g.zLabel = z_label

        dic = {'__dic_x__': str_dic_x,
               '__dic_y__': str_dic_y,
               '__z_round__': str(z_round),
               }
        str_func = """function (point) {
            let dicX = JSON.parse('__dic_x__');
            let dicY = JSON.parse('__dic_y__');
            let x = dicX[point.x];
            let y = dicY[point.y];
            let z = parseFloat(point.z.toFixed(__z_round__));
            return '(' + x + ', ' + y + '): ' + '<b> ' + z + '</b > ';
        }"""
        g.tooltip = Util.multiple_replace(dic, str_func)

        str_func = """function(value) {
            let dicX=JSON.parse('__dic_x__');
            return dicX[value];
        }"""
        g.xValueLabel = Util.multiple_replace(dic, str_func)

        str_func = """function(value) {
            let dicY=JSON.parse('__dic_y__');
            return dicY[value];
        }"""
        g.yValueLabel = Util.multiple_replace(dic, str_func)

        filename = None
        if save:
            # prepare save
            if not os.path.exists(folder_save):
                os.makedirs(folder_save)
            if not name:
                name = 'plot'
            tag = ''
            if tagged:
                tag = dt.datetime.now().strftime('_%Y%m%d_%H%M%S')
            suffix = '.html'
            filename = '{}{}{}'.format(name, tag, suffix)

        html = g.plot(df_data,
                      save=save,
                      save_path=folder_save,
                      save_name=filename)
        return html
