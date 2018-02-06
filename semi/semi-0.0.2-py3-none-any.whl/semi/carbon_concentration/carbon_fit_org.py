# -*- coding: utf-8 -*-

"""
Created on Tue Aug 18 07:42:27 2015

@author: twagner
"""

import glob
import lmfit
# import matplotlib.pyplot as plt
import os
import sys

from numpy import linspace
from numpy import argmin
from numpy import min, max
from numpy import where
from numpy import sqrt, pi, log, exp

###############################################################################
from ono.bruker_opus_filereader import OpusReader

###############################################################################
class CarbonFit:
    def __init__(self, ingot=None, wafer=None):
        '''
        initialise carbon fit:
            - set data path
            - init reference and sample spectra if ingot and wafer are given
            - set carbon coeff.
        '''

        sys.stdout.write("Initialising carbon fit ... \n")

        self.dataPath = '\\\\fcmfs1\\MT-Messdaten\\Kohlenstoff\\Daten'
        self.refPath = os.path.join(self.dataPath, "Testproben")

        self.refDate = None

        if ingot and wafer:
            self.initSample(ingot, wafer)

        self.f300 = 1.28E+16

        sys.stdout.write("Done.\n")
        # flushing stdout causes the COM server to fail !!!
        # unknown error: 0x80004005 (E_FAIL)
        # sys.stdout.flush()

    def initRef(self, date):
        self.refDate = date

        filename = "Abs_119_624_" + date + ".0"
        refFile = os.path.join(self.refPath, filename)
        
        sys.stdout.write("Loading reference spectrum: " + refFile + "\n")
                
        ref = OpusReader(refFile)
        ref.readDataBlocks()

        # self.ref = ref.I
        self.ref = ref['AB']
        
        # sys.stdout.write("Done.\n")
        

    def initSample(self, ingot, wafer):
        # date = '2014_09_04'
        date = '*'

        if ingot == '119':
            samplePath = self.refPath
        else:
            ingotRange = ingot[0:2] + '000 bis ' + ingot[0:2] + '999'
            samplePath =  os.path.join(self.dataPath, ingotRange)

        filename = 'Abs_' + ingot + '_' + wafer + '_' + date + '.0'
        fullPattern = os.path.join(samplePath, filename)

        filenameList = glob.glob(fullPattern)
        
        if len(filenameList) > 0:
            filename = filenameList[0]
            filenamePrefix = filename.split('.')[0]

            self.sampleDate = filenamePrefix[-10:]
    
            if (self.sampleDate != self.refDate):
                self.initRef(self.sampleDate)
    
            sampleFile = os.path.join(samplePath, filename)
    
            sys.stdout.write("Loading sample spectrum: " + sampleFile + "\n")
    
            sample = OpusReader(sampleFile)
            sample.readDataBlocks()
    
            # print(sample)
    
            # self.sample = sample.I
            # self.wavenumber = sample.waveNumber

            self.sample = sample['AB']
            
            fxv = sample['AB Data Parameter']['FXV']
            lxv = sample['AB Data Parameter']['LXV']
            npt = sample['AB Data Parameter']['NPT']
            self.wavenumber = linspace(fxv, lxv, npt)

            self.wMin = min(self.wavenumber)
            self.wMax = max(self.wavenumber)

            return True

        else:
            sys.stdout.write("Sample spectrum not found: " +
                fullPattern + "\n")
                
            return False
        
    def fitSequence(self):
        sys.stdout.write("Fitting sample spectrum to model ... ")

        self.chSqrList = []    
        mList = []
        nList = []

        self.cRefList = linspace(0.5, 1.5, 51)    
    
        eps = 0.01
    
        FWHM = 1.6
        Sigma = FWHM / 2. / sqrt(2. * log(2.))
    
        params = lmfit.Parameters()
        params.add('Mu', value = 579.65, vary = False)
        params.add('Sigma', value = Sigma, vary = False)
        params.add('Gamma', expr = '2 * sqrt(2 * log(2.)) * Sigma')
        params.add('Peak', value = 1.0)
    
        fwhm = 2.0
        sigma = fwhm / 2. / sqrt(2. * log(2.))
    
        params.add('mu', value = 576.3, vary = False)
        params.add('sigma', value = sigma, vary = False)
        params.add('gamma', expr = '2 * sqrt(2 * log(2.)) * sigma')
        params.add('peak', value = 1.0)
    
        params.add('m', value = 0.01)
        params.add('n', value = 0.1)
        params.add('p', value = 0.4, vary = False)

        for cRef in self.cRefList:    
            diff = self.sample - cRef * self.ref
            
            result = lmfit.minimize(residual, params,
                                    args = (self.wavenumber, diff, eps))
                                    
            self.chSqrList.append(result.chisqr)
            mList.append(result.values['m'])
            nList.append(result.values['n'])

        sys.stdout.write("Done.\n")

        iMin = argmin(self.chSqrList)
    
        self.cRef = self.cRefList[iMin]
        self.baseLine_m = mList[iMin]
        self.baseLine_n = nList[iMin]

        self.refBaseline = baseline(self.wavenumber,
                                    self.baseLine_m, self.baseLine_n)
    
        self.diff = self.sample - self.cRef * self.ref
        self.absorption = self.diff - self.refBaseline

        self.calcCarbonContent()

    def fitSpectra(self, sampleFile, refFile):
        ### read reference file
        ref = OpusReader(refFile)
        ref.readDataBlocks()

        # self.ref = ref.I
        self.ref = ref['AB']
        
        ### read sample file
        sample = OpusReader(sampleFile)
        sample.readDataBlocks()

        # print(sample)
    
        # self.sample = sample.I
        # self.wavenumber = sample.waveNumber
        
        self.sample = sample['AB']
            
        fxv = sample['AB Data Parameter']['FXV']
        lxv = sample['AB Data Parameter']['LXV']
        npt = sample['AB Data Parameter']['NPT']
        self.wavenumber = linspace(fxv, lxv, npt)

        self.wMin = min(self.wavenumber)
        self.wMax = max(self.wavenumber)

        ### execute fit
        self.fit()

    def fit(self):
        sys.stdout.write("Fitting sample spectrum to model ... \n")

        self.chSqrList = []    
        mList = []
        nList = []

        self.cRefList = []   
    
        eps = 0.01
    
        FWHM = 1.6
        Sigma = FWHM / 2. / sqrt(2. * log(2.))
    
        params = lmfit.Parameters()
        params.add('Mu', value = 579.65, vary = False)
        params.add('Sigma', value = Sigma, vary = False)
        params.add('Gamma', expr = '2 * sqrt(2 * log(2.)) * Sigma')
        params.add('Peak', value = 1.0)
    
        fwhm = 2.0
        sigma = fwhm / 2. / sqrt(2. * log(2.))
    
        params.add('mu', value = 576.3, vary = False)
        params.add('sigma', value = sigma, vary = False)
        params.add('gamma', expr = '2 * sqrt(2 * log(2.)) * sigma')
        params.add('peak', value = 1.0)
    
        params.add('m', value = 0.01)
        params.add('n', value = 0.1)
        params.add('p', value = 0.4, vary = False)

        # start at cRef = 0.5
        cRef = 0.5
        diff = self.sample - cRef * self.ref
            
        self.result = lmfit.minimize(residual, params,
                                args = (self.wavenumber, diff, eps))

        self.chiSqr = self.result.chisqr

        deltacRef = 0.1
        cRef += deltacRef
        deltaChiSqr = 1.

        iCounter = 0

        print(" #    Chi^2     cRef")
        print("--------------------")

        while((abs(deltaChiSqr) > 0.001) and
            (iCounter < 100)):

            diff = self.sample - cRef * self.ref
            
            self.result = lmfit.minimize(residual, params,
                                    args = (self.wavenumber, diff, eps))

            self.cRefList.append(cRef)
            mList.append(self.result.params['m'].value)
            nList.append(self.result.params['n'].value)

            deltaChiSqr = self.result.chisqr - self.chiSqr

            if deltaChiSqr < 0.:
                pass
            else:
                deltacRef = - 0.5 * deltacRef
                
            self.chiSqr = self.result.chisqr

            print ("%2d %8.3f %8.3f" % (iCounter, self.chiSqr, cRef))
                                    
            self.chSqrList.append(self.result.chisqr)

            cRef += deltacRef
            iCounter += 1

        sys.stdout.write("Done.\n")

        iMin = argmin(self.chSqrList)
    
        self.cRef = self.cRefList[iMin]
        self.baseLine_m = mList[iMin]
        self.baseLine_n = nList[iMin]

        self.refBaseline = baseline(self.wavenumber,
                                    self.baseLine_m, self.baseLine_n)
    
        self.diff = self.sample - self.cRef * self.ref
        self.absorption = self.diff - self.refBaseline

        self.calcCarbonContent()

        
    def calcCarbonContent(self):
        sys.stdout.write("Calculating carbon content ... ")
        self.absMax = max(self.absorption)
        dFWHM = 0.5 * self.absMax
        iFWHM = where(self.absorption > dFWHM)
        
        i1 = iFWHM[0][0] - 1
        i2 = iFWHM[0][0]
        i3 = iFWHM[0][-1]
        i4 = iFWHM[0][-1] + 1
    
        w1 = self.wavenumber[i1]
        w2 = self.wavenumber[i2]
        w3 = self.wavenumber[i3]
        w4 = self.wavenumber[i4]
    
        s1 = self.absorption[i1]
        s2 = self.absorption[i2]
        s3 = self.absorption[i3]
        s4 = self.absorption[i4]
    
        wLeft = w1 + (w2 - w1) / (s2 - s1) * (dFWHM - s1)
        wRight = w3 + (w4 - w3) / (s4 - s3) * (dFWHM - s3)
        self.wFWHM = wLeft - wRight
    
        self.cCarbon = self.f300 * self.absMax * self.wFWHM
        sys.stdout.write("Done.\n")
        
        sys.stdout.write("cC = " + str(self.cCarbon) + "\n")
        
################################################################################
def residual(params, x, data, eps_data):
    return (data - model(params, x)) / eps_data


def model(params, x):
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

###############################################################################
# def main():
if __name__ == "__main__":
    '''
    stab = 'G0007'
    scheibe = 'K1'

    carbon = CarbonFit(stab, scheibe)
    carbon.fit()
    '''

    carbon = CarbonFit()

    filepath = "\\\\fcmfs1\\MT-Messdaten\\Kohlenstoff\\Daten\\Testproben"
    
    filename = "Abs_119_624_2015_12_07.1"
    ref = os.path.join(filepath, filename)
    
    filename = "Abs_119_626_2015_12_07.1"
    sample = os.path.join(filepath, filename)
    
    carbon.fitSpectra(sample, ref)
    
    ###########################################################################
    # do all plots
    ###########################################################################
    import matplotlib.pyplot as plt
    
    plt.close('all')
    plt.subplot(3,1,1)
    plt.plot(carbon.wavenumber, carbon.cRef * carbon.ref + carbon.refBaseline)
    plt.plot(carbon.wavenumber, carbon.sample)
    plt.xlim((carbon.wMax, carbon.wMin))
    
    plt.subplot(3,1,2)
    plt.plot(carbon.wavenumber, carbon.diff)
    plt.plot(carbon.wavenumber, carbon.refBaseline, color = 'r', linewidth = 2)
    plt.plot(carbon.wavenumber, model(carbon.result.params, carbon.wavenumber),
             color = 'k', linewidth = 2)
             
    plt.xlim((carbon.wMax, carbon.wMin))
    # plt.xlabel('wave number [cm$^{-1}$]')

    plt.subplot(3,1,3)
    plt.plot(carbon.wavenumber, carbon.absorption)
    plt.xlim((carbon.wMax, carbon.wMin))
    plt.xlabel('wave number [cm$^{-1}$]')

    plt.tight_layout()

    plt.figure()
    plt.plot(carbon.cRefList, carbon.chSqrList, '.')
    plt.xlabel('fraction of reference specrum $c_\mathrm{ref}$')
    plt.ylabel(r'$\chi^2$')

###############################################################################
# if __name__ == "__main__":
#    main()

