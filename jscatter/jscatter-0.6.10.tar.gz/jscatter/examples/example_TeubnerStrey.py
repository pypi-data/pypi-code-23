import jscatter as js
import numpy as np

# TeubnerStrey model for microemulsions

q=js.loglist(0.1,5,200)
p=js.grace()
for d,xi in zip([20,10,10,10,10],[20,20,10,4,1]):
    TB=js.ff.teubnerStrey(q,xi,d,eta2=1)
    p.plot(TB,symbol=0,line=[1,2,-1],legend='d=%.2g xi=%.2g' %(d,xi))
p.yaxis(scale='l',label='I(Q)',charsize=1.5)
p.xaxis(0.1,5,scale='l',label='Q / nm\S-1',charsize=1.5)
p.legend(x=0.2,y=0.8)
p.title('Teubner Strey model for microemulsions')
