# -*- coding: utf-8 -*-

'''
Wikipedia:
    Transmittance: T = I / I_0
    Absorbance: A = -log_10 (T)
'''

import logging
import lmfit

### import from ###############################################################
from numpy import argmin, exp, log
from numpy import pi, sqrt
from numpy import where

logging.getLogger('carbon').addHandler(logging.NullHandler)

###############################################################################
class CarbonFit:
    def __init__(self, wavenumbers, reference, sample):
        self.logger = logging.getLogger('carbon')
        
        self.wavenumbers = wavenumbers
        self.ref = reference
        self.sample = sample

        self.wMin = min(self.wavenumbers)
        self.wMax = max(self.wavenumbers)

        self.init_fit_parameters()


    def init_fit_parameters(self):

        FWHM = 1.6
        Sigma = FWHM / 2. / sqrt(2. * log(2.))

        self.params = lmfit.Parameters()
        self.params.add('Mu', value = 579.65, vary = False)
        self.params.add('Sigma', value = Sigma, vary = False)
        self.params.add('Gamma', expr = '2 * sqrt(2 * log(2.)) * Sigma')
        self.params.add('Peak', value = 1.0)

        fwhm = 2.0
        sigma = fwhm / 2. / sqrt(2. * log(2.))
    
        self.params.add('mu', value = 576.3, vary = False)
        self.params.add('sigma', value = sigma, vary = False)
        self.params.add('gamma', expr = '2 * sqrt(2 * log(2.)) * sigma')
        self.params.add('peak', value = 1.0)

        self.params.add('m', value = 0.01)
        self.params.add('n', value = 0.1)
        self.params.add('p', value = 0.4, vary = False)


    def fit(self):
        self.logger.debug("Fitting sample spectrum to model")

        self.chSqrList = []    
        mList = []
        nList = []

        self.cRefList = []   
    
        eps = 0.01

        # start at cRef = 0.5
        cRef = 0.5
        diff = self.sample - cRef * self.ref
            
        self.result = lmfit.minimize(residual, self.params,
                                args = (self.wavenumbers, diff, eps))

        self.chiSqr = self.result.chisqr

        deltacRef = 0.1
        cRef += deltacRef
        deltaChiSqr = 1.

        iCounter = 0

        self.logger.debug(" #    Chi^2     cRef")
        self.logger.debug("--------------------")

        while((abs(deltaChiSqr) > 0.001) and
            (iCounter < 100)):

            diff = self.sample - cRef * self.ref
            
            self.result = lmfit.minimize(residual, self.params,
                                    args=(self.wavenumbers, diff, eps))

            self.cRefList.append(cRef)
            mList.append(self.result.params['m'].value)
            nList.append(self.result.params['n'].value)

            deltaChiSqr = self.result.chisqr - self.chiSqr

            if deltaChiSqr < 0.:
                pass
            else:
                deltacRef = - 0.5 * deltacRef
                
            self.chiSqr = self.result.chisqr

            self.logger.debug("%2d %8.3f %8.3f", iCounter, self.chiSqr, cRef)
                                    
            self.chSqrList.append(self.result.chisqr)

            cRef += deltacRef
            iCounter += 1

        iMin = argmin(self.chSqrList)
    
        self.cRef = self.cRefList[iMin]
        self.baseLine_m = mList[iMin]
        self.baseLine_n = nList[iMin]

        self.refBaseline = baseline(
                self.wavenumbers, self.baseLine_m, self.baseLine_n)
    
        self.diff = self.sample - self.cRef * self.ref
        self.absorption = self.diff - self.refBaseline

        self.absorption_model = (
            carbon_absorption_model(self.result.params, self.wavenumbers)
            - self.refBaseline)
        
        self.cCarbon, self.absMax, self.wFWHM, self.wRight = calcCarbonContent(
                self.wavenumbers,
                self.absorption_model)


def calcCarbonContent(wavenumbers, absorption):
    f300 = 1.28E+16
    cCarbon_ref = 4.6E+13
    
    logger = logging.getLogger('carbon')
    logger.debug("Calculating carbon content ... ")
    absMax = max(absorption)
    dFWHM = 0.5 * absMax
    iFWHM = where(absorption > dFWHM)
    
    i1 = iFWHM[0][0] - 1
    i2 = iFWHM[0][0]
    i3 = iFWHM[0][-1]
    i4 = iFWHM[0][-1] + 1

    w1 = wavenumbers[i1]
    w2 = wavenumbers[i2]
    w3 = wavenumbers[i3]
    w4 = wavenumbers[i4]

    s1 = absorption[i1]
    s2 = absorption[i2]
    s3 = absorption[i3]
    s4 = absorption[i4]

    wLeft = w1 + (w2 - w1) / (s2 - s1) * (dFWHM - s1)
    wRight = w3 + (w4 - w3) / (s4 - s3) * (dFWHM - s3)
    wFWHM = wLeft - wRight

    cCarbon = f300 * absMax * wFWHM + cCarbon_ref
    
    logger.info("cC = %8.2e 1/ccm"  % cCarbon)

    return cCarbon, absMax, wFWHM, wRight
        
###############################################################################
def residual(params, x, data, eps_data):
    return (data - carbon_absorption_model(params, x)) / eps_data

###############################################################################
def carbon_absorption_model(params, x):
    # baseline
    m = params['m'].value
    n = params['n'].value
    
    # Gauss
    Mu = params['Mu'].value
    Sigma = params['Sigma'].value

    # Lorentz-Peak
    value = params['Gamma'].value

    if value is None:
        Gamma = eval(params['Gamma'].expr)
    else:
        Gamma = params['Gamma'].value

    # height of major Gauss-Lorentz-Peak
    Peak = params['Peak'].value

    # Gauss
    mu = params['mu'].value
    sigma = params['sigma'].value

    # Lorentz-Peak
    value = params['gamma'].value

    if value is None:
        gamma = eval(params['gamma'].expr)
    else:
        gamma = params['gamma'].value


    # height of minor Gauss-Lorentz-Peak
    peak = params['peak'].value

    # weight between Lorentz and Gauss
    p = params['p'].value

    y = (
        Peak * gauss_cauchy(x, Mu, Sigma, Gamma, p) +
        peak * gauss_cauchy(x, mu, sigma, gamma, p) +
        baseline(x, m, n)
        )

    return y


def cauchy(x, mu = 0.0, gamma = 1.0):
    y = 1. / pi / gamma / (1 + (x - mu)**2 / gamma**2)
    return y


def gauss(x, mu = 0.0, sigma = 1.0):
    y = 1. / sigma / sqrt(2 * pi) * exp(-0.5 * (x - mu)**2 / sigma**2)
    return y


def gauss_cauchy(x, mu = 0.0, sigma = 1.0, gamma = 1.0, p = 0.5):
    y = p * cauchy(x, mu, gamma) + (1 - p) * gauss(x, mu, sigma)
    return y


def baseline(x, m = 1.0, n = 0.0):
    y = m * x + n
    return y

