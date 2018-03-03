import pygsti
import plotly
import pickle
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np

# Create random data with numpy
N = 1000
random_x = np.random.randn(N)
random_y = np.random.randn(N)

# Create a trace
trace = go.Scatter(
    x = random_x,
    y = random_y,
    mode = 'markers'
)
data = [trace]
fig = go.Figure(data=[trace], layout={}) #trace

pygsti.report.workspace.enable_plotly_pickling()

print "plotly version = ",plotly.__version__

x = fig #['layout']
#del x._parent
print "dir = ",dir(x)
print "type = ",type(x)
print "class = ",x.__class__

#def getstate(self):
#    print("GETSTATE!!!")
#    return {} #self.__dict__
#def reduce(self):
#    print("REDUCD!!!")
#    return (plotly.graph_objs.graph_objs.Figure,
#                (), self.__dict__)
#def copy(self):
#    print("COPY")
#    return self
#x.__class__.__getstate__ = getstate
#x.__class__.__reduce__ = reduce
##x.__class__.__copy__ = copy

#import dill
#dill.detect.trace(True)
#dill.detect.badobjects(x, depth=1)

#try:
s = pickle.dumps(x)
print "x: ",type(x), "OK"
x2 = pickle.loads(s)
print x
#print "parent = ",x._parent
#except:
#    print "x: ",type(x), "ERR"

#for m in dir(x): #.__dict__:
#    try:
#        s = pickle.dumps(getattr(x,m))
#        print m,"OK"
#    except:
#        print m,"ERR"
#
#s = pickle.dumps(x)

#print("layout",type(fig['layout']))
#s = pickle.dumps(fig['layout'])
#print("data",type(fig['data']))
#s = pickle.dumps(fig['data'])
