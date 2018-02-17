import jscatter as js
import numpy as np

# prepare profiles SANS for typical 2m and 8m measurement
# smear calls resFunc with the respective parameters; smear also works with line collimation SAXS if needed
resol2m = js.sas.prepareBeamProfile('SANS', detDist=2000, collDist=2000., wavelength=0.4, wavespread=0.15)
resol8m = js.sas.prepareBeamProfile('SANS', detDist=8000, collDist=8000., wavelength=0.4, wavespread=0.15)

# demonstration smearing effects

# generate some data, or load them from measurement
a,b=2,3
obj=js.dL()
temp=js.ff.ellipsoid(np.r_[0.01:1:0.01],a,b)
temp.Y+=2 # add background
obj.append(js.sas.smear(temp, resol8m))
temp=js.ff.ellipsoid(np.r_[0.5:5:0.05],a,b)
temp.Y+=2
obj.append(js.sas.smear(temp, resol2m))

# here we compare the difference between the 2 profiles using for both the full q range
obj2=js.dL()
temp=js.ff.ellipsoid(np.r_[0.01:5:0.01],a,b)
temp.Y+=2
obj2.append(js.sas.smear(temp, resol8m))
temp=js.ff.ellipsoid(np.r_[0.01:5:0.01],a,b)
temp.Y+=2
obj2.append(js.sas.smear(temp, resol2m))

# plot it
p=js.grace()
ellip=js.ff.ellipsoid(np.r_[0.01:5:0.01],a,b)
ellip.Y+=2
p.plot(ellip,sy=[1,0.3,1],legend='unsmeared ellipsoid')
p.yaxis(label='Intensity / a.u.',scale='l')
p.xaxis(label='Q / nm\S-1',scale='n')
p.plot(obj,legend='smeared $rf_detDist')
p.plot(obj2[0],li=[1,1,4],sy=0,legend='8m smeared full range')
p.plot(obj2[1],li=[3,1,4],sy=0,legend='2m smeared full range')
p.legend(x=2.5,y=8000)
p.title('SANS smearing of ellipsoid')
#p.save('SANSsmearing.jpg')

# now we use the simulated data to fit this to a model

# first possibility
# obj has the information about the used settings in rf_detDist (set in resFunct )
# for experimental data this needs to be added to the loaded data
# another possibility is to use resFunc directly and have the detDist attribute in the data as shown below
def smearedellipsoid(q,A,a,b,rf_detDist,bgr):
    ff=js.ff.ellipsoid(q,a,b)  # calc model
    ff.Y=ff.Y*A+bgr  # multiply amplitude factor and add bgr
    # smear
    if rf_detDist==2000:
        ffs=js.sas.smear(ff, resol2m)
    elif rf_detDist==8000:
        ffs=js.sas.smear(ff, resol8m)
    elif rf_detDist==0:
        # this shows unsmeared model
        ffs=ff
    return ffs

# fit it , here no errors
obj.makeErrPlot(yscale='l',fitlinecolor=[1,2,5])
obj.fit(smearedellipsoid,{'A':1,'a':2.5,'b':3.5,'bgr':0},{},{'q':'X'})
# show the unsmeared model
obj.errPlot(obj.modelValues(rf_detDist=0),li=[3,2,4],sy=0,legend='unsmeared fit')

if 0:
    # second possibility for model: use resFunc directly
    obj[0].detDist=8000   # set detDist for your data
    obj[1].detDist=2000

    def smearedellipsoid2(q,A,a,b,detDist,bgr):
        ff=js.ff.ellipsoid(q,a,b)  # calc model
        ff.Y=ff.Y*A+bgr  # multiply amplitude factor and add bgr
        # smear
        if detDist>0:
            ffs=js.sas.resFunct(ff, detDist=detDist, collDist=detDist, wavelength=0.4, wavespread=0.15)
        elif detDist==0:
            # this shows unsmeared model
            ffs=ff
        return ffs

    # fit it , here no errors
    obj.makeErrPlot(yscale='l',fitlinecolor=5)
    obj.fit(smearedellipsoid2,
            {'A':1,'a':2.5,'b':2.5,'bgr':0},{},{'q':'X'})
