import jscatter as js
from jscatter.graceplot import *

#make some data
x1=np.r_[0:10:0.1]
y1=np.sin(x1)
y2=np.cos(x1)

p = js.grace() # A grace session opens
p.multi(2,1)
#the SHORT way
p.plot(x1,y1,sy=[1,0.5,2])
p.plot(x1,y2,sy=[1,0.5,4])
#the long old way

# original idea to create symbols and lines and data object
l1=Line(type=lines.none)    # or l1=Line(type=0)
d2=Data(x=x1,y=y1, bsymbol=Symbol(symbol=symbols.circle,fillcolor=colors.red), line=l1)
d3=Data(x=x1,y=y2, symbol=Symbol(symbol=symbols.circle,fillcolor=colors.blue), line=l1)

g=p[1]
g.plot(d2,d3)
g.xaxis(label=Label('X axis',font=5,charsize=1.5),
        tick=Tick(majorgrid=True,majorlinestyle=lines.dashed,majorcolor=colors.blue,
                  minorgrid=True,minorlinestyle=lines.dotted,minorcolor=colors.blue))
g.yaxis(tick=Tick(majorgrid=True,majorlinestyle=lines.dashed,majorcolor=colors.blue,
                  minorgrid=True,minorlinestyle=lines.dotted,minorcolor=colors.blue))

p[0].title('grace2 example')
