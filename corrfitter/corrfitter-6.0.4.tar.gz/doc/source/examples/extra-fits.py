from __future__ import print_function   # makes this work for python2 and 3

import collections
import sys

import gvar as gv
import numpy as np
import corrfitter as cf


if sys.argv[1:]:
    DISPLAYPLOTS = eval(sys.argv[1]) # display plots at end of fitting?
    try:
        import matplotlib
    except ImportError:
        DISPLAYPLOTS = False
else:
    DISPLAYPLOTS = False

def main():
    fitter = cf.CorrFitter(
        models=make_models(), fitter='gsl_multifit', alg='subspace2D', scaler='more', solver='cholesky'
        )
    pdata = make_pdata('extra-fits.data', fitter.models)
    p0 = None
    prior = make_prior(20)
    for N in [3]:
        print(30 * '=', 'nterm =', N)
        prior = make_prior(N)
        fit = fitter.lsqfit(pdata=pdata, prior=prior, p0=p0, nterm=(N,N-1), svdcut=1e-3)
        p0 = fit.pmean
        print(fit.formatall())
    print_results(fit, prior, pdata)
    if DISPLAYPLOTS:
        fitter.display_plots()

def make_pdata(filename, models):
    dataset = cf.read_dataset(filename)
    return cf.process_dataset(dataset, models)

def make_models():
    """ Create models to fit data. """
    tmin = 2
    tp = 64
    ncg = 1
    models = [
        cf.Corr2(
            datatag='etas', tp=tp,  tmin=tmin, tmax=15,
            a=('etas:a','etaso:a'),  b=('etas:a','etaso:a'),  dE=('etas:dE','etaso:dE')
            ),

        cf.Corr2(
            datatag='Ds', tp=tp,  tmin=tmin,
            a=('Ds:a', 'Dso:a'), b=('Ds:a', 'Dso:a'),
            dE=('Ds:dE', 'Dso:dE'), s=(1., -1.)
            ),

        cf.Corr3(
            datatag='DsetasT15', T=15, tmin=tmin,
            a=('etas:a','etaso:a'),  dEa=('etas:dE','etaso:dE'),
            b=('Ds:a', 'Dso:a'), dEb=('Ds:dE', 'Dso:dE'),
            Vnn='Vnn', Vno='Vno', Von='Von', Voo='Voo', ncg=ncg,
            ),

        cf.Corr3(
            datatag='etasDsT15', T=15, tmin=tmin,
            a=('etas:a','etaso:a'),  dEa=('etas:dE','etaso:dE'),
            b=('Ds:a', 'Dso:a'), dEb=('Ds:dE', 'Dso:dE'),
            Vnn='Vnn', Vno='Vno', Von='Von', Voo='Voo', ncg=ncg, reverse=True
            ),

        ## following is equivalent to Corr3 just above (but more complicated)
        # cf.Corr3(
        #     datatag='etasDsT15', T=15, tmin=tmin,
        #     b=('etas:a','etaso:a'),  dEb=('etas:dE','etaso:dE'),
        #     a=('Ds:a', 'Dso:a'), dEa=('Ds:dE', 'Dso:dE'),
        #     Vnn='Vnn', Vno='Von', Von='Vno', Voo='Voo', ncg=ncg, transpose_V=True
        #     ),

        cf.Corr3(
            datatag='DsetasT18', T=18, tmin=tmin,
            a=('etas:a','etaso:a'),  dEa=('etas:dE','etaso:dE'),
            b=('Ds:a', 'Dso:a'), dEb=('Ds:dE', 'Dso:dE'),
            Vnn='Vnn', Vno='Vno',  Von='Von', Voo='Voo', ncg=ncg,
            reverseddata='etasDsT18'
            ),

        cf.Corr3(
            datatag='DsDsT15', T=15, tmin=tmin,
            b=('Ds:a', 'Dso:a'), dEb=('Ds:dE', 'Dso:dE'),
            a=('Ds:a', 'Dso:a'), dEa=('Ds:dE', 'Dso:dE'),
            Vnn='Unn', Vno='Uno', Voo='Uoo', ncg=ncg,
            symmetric_V=True,
            ),

        cf.Corr3(
            datatag='DsDsT18', T=18, tmin=tmin,
            b=('Ds:a', 'Dso:a'), dEb=('Ds:dE', 'Dso:dE'),
            a=('Ds:a', 'Dso:a'), dEa=('Ds:dE', 'Dso:dE'),
            Vnn='Unn', Vno='Uno', Voo='Uoo', ncg=ncg,
            symmetric_V=True,
            )

        ]
    return models

def make_prior(N):
    """ build prior """
    prior = gv.BufferDict()
    # Ds
    M = N + 1
    prior['log(Ds:a)'] = gv.log(gv.gvar(M * ['0.2(2)']))
    prior['log(Ds:dE)'] = gv.log(gv.gvar(M * ['0.5(5)']))
    prior['log(Ds:dE)'][0] = gv.log(gv.gvar('1.3(2)'))
    prior['log(Dso:a)'] = gv.log(gv.gvar(M * ['0.2(2)']))
    prior['log(Dso:dE)'] = gv.log(gv.gvar(M * ['0.5(5)']))
    prior['log(Dso:dE)'][0] = gv.log(gv.gvar('1.50(5)'))

    # etas
    prior['log(etas:a)'] = gv.log(gv.gvar(N * ['0.2(2)']))
    prior['log(etas:dE)'] = gv.log(gv.gvar(N * ['0.5(5)']))
    prior['log(etas:dE)'][0] = gv.log(gv.gvar('0.67(20)'))
    prior['log(etaso:a)'] = gv.log(gv.gvar(N * ['0.2(2)']))
    prior['log(etaso:dE)'] = gv.log(gv.gvar(N * ['0.5(5)']))
    prior['log(etaso:dE)'][0] = gv.log(gv.gvar('0.88(20)'))

    # etas -> Ds
    prior['Vno'] = gv.gvar(N * [M * ['0.1(1.0)']])
    prior['Vnn'] = gv.gvar(N * [M * ['0.1(1.0)']])
    prior['Voo'] = gv.gvar(N * [M * ['0.1(1.0)']])
    prior['Von'] = gv.gvar(N * [M * ['0.1(1.0)']])

    # Ds -> Ds
    prior['Uno'] = gv.gvar(M * [M * ['0.1(1.0)']])
    prior['Unn'] = gv.gvar((M * (M + 1)) // 2 * ['0.1(1.0)'])
    prior['Uoo'] = gv.gvar((M * (M + 1)) // 2 * ['0.1(1.0)'])
    prior['Uon'] = gv.gvar(M * [M * ['0.1(1.0)']])

    return prior

def print_results(fit, prior, data):
    """ Report best-fit results. """
    print('Fit results:')
    p = fit.p                       # best-fit parameters

    # etas
    E_etas = np.cumsum(p['etas:dE'])
    a_etas = p['etas:a']
    print('  Eetas:', E_etas[:3])
    print('  aetas:', a_etas[:3])

    # Ds
    E_Ds = np.cumsum(p['Ds:dE'])
    a_Ds = p['Ds:a']
    print('\n  EDs:', E_Ds[:3])
    print(  '  aDs:', a_Ds[:3])

    # Dso -- oscillating piece
    E_Dso = np.cumsum(p['Dso:dE'])
    a_Dso = p['Dso:a']
    print('\n  EDso:', E_Dso[:3])
    print(  '  aDso:', a_Dso[:3])

    if 'Vnn' in p:
        # V
        Vnn = p['Vnn']
        Vno = p['Vno']
        print('\n  etas->V->Ds  =', Vnn[0, 0])
        print('  etas->V->Dso =', Vno[0, 0])

    if 'Unn' in p:
        Unn = p['Unn'][0]
        print('\n  Ds->U->Ds =', Unn)

    # error budget
    outputs = collections.OrderedDict()
    outputs['metas'] = E_etas[0]
    outputs['mDs'] = E_Ds[0]
    outputs['mDso-mDs'] = E_Dso[0] - E_Ds[0]
    if 'Vnn' in p:
        outputs['Vnn'] = Vnn[0, 0]
        outputs['Vno'] = Vno[0, 0]

    if 'Unn' in p:
        outputs['Unn'] = Unn

    inputs = collections.OrderedDict()
    inputs['statistics'] = data                 # statistical errors in data
    inputs.update(prior)                        # all entries in prior
    inputs['svd'] = fit.svdcorrection           # svd cut (if present)

    print('\n' + gv.fmt_values(outputs))
    print(gv.fmt_errorbudget(outputs, inputs))
    print('\n')

if __name__ == '__main__':
    main()

"""
============================== nterm = 3
Least Square Fit:
  chi2/dof [dof] = 0.61 [116]    Q = 1    logGBF = 2810.1

Parameters:
  log(etas:a) 0   -1.7616 (92)      [ -1.6 (1.0) ]
              1     -1.62 (25)      [ -1.6 (1.0) ]
              2    -0.695 (98)      [ -1.6 (1.0) ]
 log(etas:dE) 0   -0.3994 (22)      [ -0.40 (30) ]
              1     -0.71 (18)      [ -0.7 (1.0) ]
              2     -0.41 (15)      [ -0.7 (1.0) ]
 log(etaso:a) 0     -3.05 (27)      [ -1.6 (1.0) ]  *
              1     -2.83 (20)      [ -1.6 (1.0) ]  *
log(etaso:dE) 0    -0.218 (33)      [ -0.13 (23) ]
              1     -1.76 (58)      [ -0.7 (1.0) ]  *
    log(Ds:a) 0   -1.5608 (55)      [ -1.6 (1.0) ]
              1     -1.72 (22)      [ -1.6 (1.0) ]
              2    -0.694 (65)      [ -1.6 (1.0) ]
   log(Ds:dE) 0   0.27071 (53)      [  0.26 (15) ]
              1     -1.02 (16)      [ -0.7 (1.0) ]
              2    -0.784 (82)      [ -0.7 (1.0) ]
   log(Dso:a) 0     -2.66 (10)      [ -1.6 (1.0) ]  *
              1     -2.10 (16)      [ -1.6 (1.0) ]
  log(Dso:dE) 0    0.3504 (92)      [ 0.405 (33) ]  *
              1     -1.15 (24)      [ -0.7 (1.0) ]
        Vnn 0,0    0.1368 (15)      [  0.1 (1.0) ]
            0,1    -0.065 (23)      [  0.1 (1.0) ]
            0,2    -0.065 (41)      [  0.1 (1.0) ]
            1,0     0.008 (12)      [  0.1 (1.0) ]
            1,1      0.08 (99)      [  0.1 (1.0) ]
            1,2    0.09 (1.00)      [  0.1 (1.0) ]
            2,0     0.006 (35)      [  0.1 (1.0) ]
            2,1      0.2 (1.0)      [  0.1 (1.0) ]
            2,2      0.1 (1.0)      [  0.1 (1.0) ]
        Vno 0,0    -0.065 (13)      [  0.1 (1.0) ]
            0,1    -0.072 (33)      [  0.1 (1.0) ]
            1,0      0.66 (13)      [  0.1 (1.0) ]
            1,1      0.2 (1.0)      [  0.1 (1.0) ]
            2,0     -0.26 (51)      [  0.1 (1.0) ]
            2,1    0.08 (1.00)      [  0.1 (1.0) ]
        Von 0,0    -0.027 (55)      [  0.1 (1.0) ]
            0,1      1.49 (31)      [  0.1 (1.0) ]  *
            0,2     -0.79 (49)      [  0.1 (1.0) ]
            1,0    -0.088 (65)      [  0.1 (1.0) ]
            1,1      0.25 (98)      [  0.1 (1.0) ]
            1,2    0.06 (1.00)      [  0.1 (1.0) ]
        Voo 0,0     -1.64 (25)      [  0.1 (1.0) ]  *
            0,1     -0.06 (44)      [  0.1 (1.0) ]
            1,0      0.27 (57)      [  0.1 (1.0) ]
            1,1     -0.1 (1.0)      [  0.1 (1.0) ]
          Unn 0    0.1053 (26)      [  0.1 (1.0) ]
              1     0.009 (20)      [  0.1 (1.0) ]
              2    -0.039 (37)      [  0.1 (1.0) ]
              3      0.1 (1.0)      [  0.1 (1.0) ]
              4      0.1 (1.0)      [  0.1 (1.0) ]
              5      0.1 (1.0)      [  0.1 (1.0) ]
        Uno 0,0   -0.2171 (80)      [  0.1 (1.0) ]
            0,1     0.033 (47)      [  0.1 (1.0) ]
            1,0     -0.08 (11)      [  0.1 (1.0) ]
            1,1      0.1 (1.0)      [  0.1 (1.0) ]
            2,0      0.10 (16)      [  0.1 (1.0) ]
            2,1      0.1 (1.0)      [  0.1 (1.0) ]
          Uoo 0    -0.080 (79)      [  0.1 (1.0) ]
              1      0.02 (16)      [  0.1 (1.0) ]
              2      0.1 (1.0)      [  0.1 (1.0) ]
--------------------------------------------------
       etas:a 0    0.1718 (16)      [  0.20 (20) ]
              1     0.198 (50)      [  0.20 (20) ]
              2     0.499 (49)      [  0.20 (20) ]  *
      etas:dE 0    0.6707 (14)      [  0.67 (20) ]
              1     0.494 (88)      [  0.50 (50) ]
              2     0.667 (98)      [  0.50 (50) ]
      etaso:a 0     0.047 (13)      [  0.20 (20) ]
              1     0.059 (12)      [  0.20 (20) ]
     etaso:dE 0     0.804 (27)      [  0.88 (20) ]
              1     0.171 (99)      [  0.50 (50) ]
         Ds:a 0    0.2100 (12)      [  0.20 (20) ]
              1     0.178 (39)      [  0.20 (20) ]
              2     0.500 (33)      [  0.20 (20) ]  *
        Ds:dE 0   1.31089 (69)      [  1.30 (20) ]
              1     0.361 (59)      [  0.50 (50) ]
              2     0.457 (38)      [  0.50 (50) ]
        Dso:a 0    0.0699 (72)      [  0.20 (20) ]
              1     0.122 (19)      [  0.20 (20) ]
       Dso:dE 0     1.420 (13)      [ 1.500 (50) ]  *
              1     0.316 (75)      [  0.50 (50) ]

Settings:
  svdcut/n = 0.001/44    tol = (1e-08*,1e-10,1e-10)    (itns/time = 50/1.4)
  fitter = gsl_multifit    methods = subspace2D/more/cholesky

Fit results:
  Eetas: [0.6707(14) 1.165(90) 1.83(16)]
  aetas: [0.1718(16) 0.198(50) 0.499(49)]

  EDs: [1.31089(69) 1.672(60) 2.128(64)]
  aDs: [0.2100(12) 0.178(39) 0.500(33)]

  EDso: [1.420(13) 1.735(87)]
  aDso: [0.0699(72) 0.122(19)]

  etas->V->Ds  = 0.1368(15)
  etas->V->Dso = -0.065(13)

  Ds->U->Ds = 0.1053(26)

Values:
              metas: 0.6707(14)
                mDs: 1.31089(69)
           mDso-mDs: 0.109(13)
                Vnn: 0.1368(15)
                Vno: -0.065(13)
                Unn: 0.1053(26)

Partial % Errors:
                   metas       mDs  mDso-mDs       Vnn       Vno       Unn
--------------------------------------------------------------------------
   statistics:      0.18      0.05      9.61      0.63     14.22      1.03
    log(Ds:a):      0.01      0.01      0.07      0.09      0.67      0.22
   log(Ds:dE):      0.01      0.01      0.40      0.07      0.90      0.31
   log(Dso:a):      0.00      0.00      2.42      0.07      3.30      0.06
  log(Dso:dE):      0.01      0.00      4.62      0.11      5.39      0.07
  log(etas:a):      0.04      0.00      0.09      0.01      2.95      0.01
 log(etas:dE):      0.03      0.00      0.07      0.01      2.25      0.01
 log(etaso:a):      0.01      0.00      1.08      0.07      3.21      0.03
log(etaso:dE):      0.01      0.00      0.79      0.07      3.76      0.04
          Vno:      0.07      0.00      2.10      0.05      5.32      0.04
          Vnn:      0.01      0.00      0.19      0.74      0.55      0.03
          Voo:      0.01      0.00      0.85      0.17      3.68      0.11
          Von:      0.01      0.01      0.80      0.09      3.62      0.21
          Uno:      0.00      0.00      1.87      0.04      0.89      0.08
          Unn:      0.00      0.00      0.40      0.00      0.30      1.89
          Uoo:      0.01      0.00      0.47      0.01      0.27      0.42
          Uon:      0.00      0.00      0.00      0.00      0.00      0.00
          svd:      0.07      0.02      3.46      0.38      7.36      1.02
--------------------------------------------------------------------------
        total:      0.22      0.05     11.97      1.08     19.80      2.47



[Finished in 1.4s]
    """