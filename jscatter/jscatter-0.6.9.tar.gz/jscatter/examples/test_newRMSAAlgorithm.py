import numpy as np

import jscatter as js

# this example is for comparison of the original Hayter-Penfold FORTRAN code for RMSA with an improved version
# MSA solves a quartic Fwww to find the root with g(r<1)=0 which is rescaled for some conditions when g(r=0)<0.
# The root of the quartic is found by a good estimate with a Newton algorithm to refine the zero.
# The Newton algorithm finds an arbitrary root of Fwww which sometimes is completely wrong.
# The new algorithm uses the original idea of HP to calc g(r<0) and uses this to define the correct solution.
# g(r) is calculated here for r=1-delta close to r=1 with r.


# for direct comparison to Fortran build sofq.so with
#f2py -c sofq_changed.f90 -m sofqc --fcompiler=gfortran
# noinspection PyBroadException
try:
    import sofqc

    def RMSAc(q,R,e,scl,g):
        Q=np.r_[q]
        Sq=np.ones_like(Q)
        err=0
        sofqc.sofq(2*Q*R,Sq,e,scl,g,R,1,err)
        result=js.dA(np.r_[[q,Sq]])
        result.setColumnIndex(iey=None)
        return result


    # noinspection PyIncorrectDocstring
    def progf(q,R,scl,g,e):
        """this reproduces that useHP=1 and original fortran HP are the same"""
        ret=RMSAc(q=q,R=R,scl=scl, g=g, e=e)
        ret._coefficients={'g1':1,'ak':1,'f':1}
        return ret
except:
    pass

# with useHP=1 a HP equivalent code tested against the original Fortran is used
prog1=lambda q,R,scl,g,e:js.sf.RMSA(q=q,R=R,scl=scl, gamma=g, eta=e,useHP=1)
# useHP=0 uses the new algorithm
prog0=lambda q,R,scl,g,e:js.sf.RMSA(q=q,R=R,scl=scl, gamma=g, eta=e,useHP=0)

prog2=prog0
#prog2=progf  # uncomment for fortran comparison

# noinspection PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember
def compare(q=js.loglist(0.01,5,50),g=100,R=5,e=0.4,akl=np.r_[js.loglist(0.1,9,50),10:60:2]):
    p1=js.grace()
    p1[0].SetView(xmin=0.15,xmax=0.7,ymin=0.15,ymax=0.85)
    p1.new_graph(xmin=0.7,xmax=0.95,ymin=0.15,ymax=0.85)
    aklv=[]
    aklc=[]
    for cc,ak in enumerate(akl):
        c=cc+1
        scl=2*R/ak
        rc =prog1(q=q,R=R,scl=scl, g=g, e=e)
        rjs=prog2(q=q,R=R,scl=scl, g=g, e=e)
        if isinstance(rc,int) and not isinstance(rjs,int):
            mm='%.3g %.3g ir=%.f ' %(rjs._coefficients['f'],rjs._coefficients['g1'],rc)
            p1[0].plot(rjs.X*2*R,rjs.Y,sy=0,li=[1,1,c], legend='j ak%.3g ' %(rjs._coefficients['ak'])+mm)
        elif isinstance(rjs,int) and not isinstance(rc,int):
            mm='%.3g %.3g ir=%.f ' %(rc._coefficients['f'],rc._coefficients['g1'],rjs)
            p1[0].plot(rc.X*2*R,rc.Y,sy=[1,0.2,c],li=0, legend='H ak%.3g ' %(rc._coefficients['ak'])+mm)
        elif isinstance(rjs,int) and isinstance(rc,int):
            pass
        else:
            if np.isclose(rc._coefficients['f'],rjs._coefficients['f']):
                mm='f%.3g g1%.3g ' %(rjs._coefficients['f'],rjs._coefficients['g1'])
                p1[0].plot(rjs.X*2*R,rjs.Y,sy=[1,0.2,c],li=[1,1,c], legend='= ak=%.3g ' %(rc._coefficients['ak'])+mm)
            else:
                mm1='f%.3g g1%.3g ' %(rc._coefficients['f'],rc._coefficients['g1'])
                mm2='f%.3g g1%.3g ' %(rjs._coefficients['f'],rjs._coefficients['g1'])
                p1[0].plot(rc.X*2*R,rc.Y,sy=[1,0.2,c],li=0,legend='! ak%.3g ' %(rc._coefficients['ak'])+mm1)
                p1[0].plot(rjs.X*2*R,rjs.Y,sy=0,li=[1,1,c], legend='! ak%.3g ' %(rjs._coefficients['ak'])+mm2)
        # noinspection PyBroadException
        try:
            aklv.append([ak,rjs.Y[0]])
        except:
            pass
        # noinspection PyBroadException
        try:
            aklc.append([ak,rc.Y[0]])
        except:
            pass
    aklv=np.array(aklv).T
    aklc=np.array(aklc).T
    p1[1].plot(aklv[0],aklv[1],sy=[1,0.4,1],li=1)
    p1[1].plot(aklc[0],aklc[1],sy=[8,0.6,2,2])
    p1[0].legend(x=6,y=0.6,charsize=0.4)
    p1[0].yaxis(min=2e-5,max=3,scale='l',label='S(Q)')
    p1[0].xaxis(scale='l',label='2RQ')
    p1[1].xaxis(scale='l',label='ak = 2R/screeningLength')
    p1[1].yaxis(scale='l',label='S(2QR=0)')
    p1[0].text('lines new js\\n symbols old algorithm',x=0.12,y=1.5,charsize=0.7)
    p1[1].text('black new js\\n red old algorithm',x=1.5,y=max(aklv[1])/2.,charsize=0.7)
    return p1


# do some comparisons

p1=compare()
p1[0].title('scl=0.1 close to scl=1; larger scl better convergent in rescaling',size=1)
p1[0].subtitle('ak=10,15 is wrong , js uses wrong root',size=1)

    
p2=compare(g=10,R=5,e=0.01)
p2[0].title('scl=11: some without solution in fortran',size=1)

p3=compare(g=9,R=1.1,e=0.001)
p3[0].title('small scl: no solution in fortran',size=1)

p4=compare(g=3,R=3.1,e=0.4)
p4[0].title('here a large part gets the wrong root in fortran',size=1)








