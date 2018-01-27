# example in fast hurry without fine tuning of plots

import numpy as np
import jscatter as js

# read data
i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')

# define model
diffusion=lambda A,D,t,elastic,wavevector=0:A*np.exp(-wavevector**2*D*t)+elastic

# make ErrPlot to see progress of intermediate steps with residuals (updated all 2 seconds)
i5.makeErrPlot(title='diffusion model residual plot')
# fit it
i5.fit(model=diffusion,                      # the fit function
       freepar={'D':[0.2],'A':1},            # freepar with start parameters; [..] to get D depend on list element
       fixpar={'elastic':0.0},               # fixed parameters
       mapNames= {'t':'X','wavevector':'q'}, # map names of the model to names of the data
       condition=lambda a:a.X>0.01  )        # a condition to include only values with X larger 0.01

# plot it together with lastfit result
p=js.grace()
p.plot(i5,symbol=[-1,0.4,-1], legend='Q=$q')
p.plot(i5.lastfit,symbol=0,line=[1,1,-1])

p1=js.grace(2,2)                          # plot with a defined size
p1.plot(i5.q,i5.D,i5.D_err,symbol=[2,1,1,''],legend='average effective D')

# D is a list because it got list of start values in brackets [2] which is expanded to [2,2,2,2,2,2....]
