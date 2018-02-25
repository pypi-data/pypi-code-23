from __future__ import absolute_import

"""Functions to quickly display charts in a Notebook.
"""

import string
import random
import json
import copy
import pandas as pd

from IPython.core import getipython
from IPython.core.display import display, HTML
import numpy as np;

# Note that Highstock includes all Highcharts features.
HIGHCHARTS_SCRIPTS1 = "https://code.highcharts.com/highcharts.js"
HIGHCHARTS_SCRIPTS2 = """
<script src="https://code.highcharts.com/stock/highstock.js"></script>
<script src="https://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>
<script src="https://code.highcharts.com/modules/histogram-bellcurve.js"></script>
"""

def load_highcharts():
    #display(HTML(HIGHCHARTS_SCRIPTS1))
    display(HTML(HIGHCHARTS_SCRIPTS2))

# Automatically insert the script tag into your Notebook.
# Call when you import this module.
if 'IPKernelApp' in getipython.get_ipython().config:
    load_highcharts()


class HighCharts:
    TS='''<script>
Highcharts.chart('CHART_DIV', {
    navigation: { buttonOptions: { enabled: false } },
    credits: { enabled: false},
    chart: { type: 'line' ,  zoomType: 'x' },
    title: { text: 'CHART_TITLE' , zoomType:'xy' },
    subtitle: { text: 'CHART_SUB_TITLE' },
    xAxis: { title: { text: 'CHART_X_AXIS_TITLE' }, type: 'datetime'},
    yAxis: { title: { text: 'CHART_Y_AXIS_TITLE'}},
    plotOptions: {
        scatter: {
            marker: { radius: 3},
            states: {
                hover: {
                    enabled: true,
                    lineColor: 'rgb(100,100,100)'
                }
            }
        },
        line: {
            animation: true,
            dataLabels: {  enabled: false  },
            enableMouseTracking: true,
            lineWidth: 0.1,
            marker: { radius: 3} 
            },
        histogram: {
            type: 'column',
            },
            
        series: { point: { events: { click: 'CLICK_FUNCTION' } } }
        },
        DATA
});
</script>
'''
    
    @staticmethod
    def tsDF(df, x=None, cols=[], names=[], div=None, title='', subtitle='', yTitle='',xTitle='', num=1000000,
              onClick='function(){g=this;console.log(g.index, g.y, g.x)}', ctype=None, dtype='int'):
        '''
        Plot High Chart assuing the data is in panadas dataframe. 
        Provide a div if it needs to be plotted inside a div or one will be creaeted for you. 
        '''
        
        ts =HighCharts.TS;
        if ( div is None ):
            div = 'DIVchart_' + str(np.random.randint(1000000))
            ts = '<div id="{}" style="height:200px"></div>\n'.format(div) + ts

        if (type(x) == str):   xa = df[x]
        elif (x is None): xa = pd.Series(df.index)
        elif (type(x) == int): xa = df[df.columns[x]]
        else: xa = x

        dt = xa
        try:
            if (xa.astype(int)[0] > 1000000000000000000):
                dt=(xa.astype(int)/1000000)[0:num]
            elif (xa.astype(int)[0] > 1000000000000000):
                dt=(xa.astype(int)/1000)[0:num]
        except:
            pass;

        dt = [int(c) for c in dt]
        dd=[]

        for i, c in enumerate(cols):
            if ( type(c) == str):
                d=list(df[c].values[0:num])
                cn=c
            elif( type(c) == int ):
                cn=df.columns[c]
                d=list(df[cn].values[0:num])
            else:
                cn= "List "+i if names is None or i >= len(names) else names[i]
                d=c;

            dat=list(zip(dt, d))
            dd.append({'name': cn, 'data': dat })

        s = 'series: ' + pd.io.json.dumps(dd) +""
        ts= ts.replace('DATA',s)
        ts=ts.replace('CHART_DIV', div)
        ts=ts.replace('CHART_TITLE', title)
        ts=ts.replace('CHART_SUB_TITLE', subtitle)
        ts=ts.replace('CHART_Y_AXIS_TITLE', yTitle)
        ts=ts.replace('CHART_X_AXIS_TITLE', xTitle)
        ts=ts.replace("'CLICK_FUNCTION'", onClick)
        ts=ts.replace('datetime', dtype)

        if (ctype != None):
            ts=ts.replace("type: 'line'","type: '{}'".format(ctype));

        display(HTML(ts))    
        return ts;
    
    
    histHTML ='''
<script>
var data2=[[140, 1],[150, 9],[160, 15],[170, 15]]
//DATA
Highcharts.chart('container', {
    navigation: { buttonOptions: { enabled: false } },
    credits: { enabled: false},
    title: {text: 'CHART-TITLE'},
    xAxis: [{title: { text: 'X-AXIS-TITLE' }}, {title: { text: '' }}],
    yAxis: [{title: { text: '' }}, {title: { text: 'Y-AXIS-TITLE' }}],

    series: [{
        name: 'H',
        type: 'histogram',
        data: data,
        showInLegend: false, 
        xAxis: 1,
        yAxis: 1,
        baseSeries: 0,
        pointPlacement: 'between',
        binsNumber: 10
    }
    ]
});
</script>
'''
    @staticmethod
    def hist(s, bins='auto', div=None, name='', title='', yTitle='',xTitle=''):
        html = HighCharts.histHTML
        if ( div is None ):
            div = 'DIVchart_' + str(np.random.randint(1000000))
            html += '<div id="{}" style="height:200px"></div>\n'.format(div)  
            
        x,y = np.histogram(s, bins=bins)
        z=zip(y,x)
        d=str(list(z)).replace('(','[').replace(')',']')
        html = html.replace("//DATA", "data="+str(d))
        html = html.replace("CHART-TITLE", title)
        html = html.replace('X-AXIS-TITLE', xTitle)
        html = html.replace('Y-AXIS-TITLE', yTitle)
        html = html.replace('container', div)
        display(HTML(html))
