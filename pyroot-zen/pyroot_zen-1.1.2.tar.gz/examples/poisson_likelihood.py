#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Example of pyroot_zen usage, using tutorial in

https://twiki.cern.ch/twiki/bin/view/RooStats/RooStatsTutorialsApril2012

"""

from pyroot_zen import ROOT
ROOT.gROOT.batch = True

#===============================================================================

def prepare_workspace():
  ## Prepare workspace & simple counting model
  w = ROOT.RooWorkspace()
  w.factory("sum     : nexp (s[0,15], b[0,10])")
  w.factory("Poisson : pdf  (nobs[0,50], nexp)")
  w.factory("Gaussian: syst (b0[0,10], b, sigmab[1])")
  w.factory("PROD    : model(pdf, syst)")

  ## Set variables
  nobs   = 3
  nbkg   = 1
  sigmab = 0.2 # relative uncertainty
  w.var("b").val       = nbkg
  w.var("b0").val      = nbkg
  w.var("b0").constant = True
  w.var("sigmab").val  = nbkg * sigmab
  w.var("b").max       = nbkg + 5*sigmab # avoid too large range
  w.var("nobs").val    = nobs
  w.var("s").val       = nobs-nbkg

  ## make now data set and import it in the workspace
  data = ROOT.RooDataSet("data", "", {w.var("nobs")})
  data.add({w.var("nobs")})
  w.Import(data)

  ## Prepare ModelConfig
  mc = ROOT.RooStats.ModelConfig("sbModel", w)
  mc.pdf                  = 'model'
  mc.observables          = 'nobs'
  mc.parametersOfInterest = 's'
  mc.nuisanceParameters   = 'b'
  
  ## these are needed for the hypothesis tests
  poi = w.var("s")
  mc.snapshot = {poi}
  mc.globalObservables = "b0"

  ## make a prior pdf for Bayesian calculators
  w.factory("Uniform::prior_s(s)");
  mc.priorPdf = "prior_s"

  ## Prepare background-only model for HypoTest
  bModel = mc.Clone()
  bModel.name = 'bModel'
  oldval = poi.val
  poi.val = 0
  bModel.snapshot = {poi}
  poi.val = oldval

  ## Finally
  mc.Print()
  w.Import(mc)
  w.Import(bModel)
  return w, mc, data

#===============================================================================

def run_profile_likelihood_calculator(mc, data):
  ## Prepare
  calc = ROOT.RooStats.ProfileLikelihoodCalculator(data, mc)
  calc.confidenceLevel = 0.683

  ## Calculate
  intv = calc.interval
  firstPOI   = mc.parametersOfInterest.first()
  lowerLimit = intv.LowerLimit(firstPOI)
  upperLimit = intv.UpperLimit(firstPOI)
  print "68% interval on {0.name} is : [{1:.2f}, {2:.2f}]".format(firstPOI, lowerLimit, upperLimit)

  ## Plot
  c = ROOT.TCanvas("ProfileLikelihoodCalculator")
  c.ownership = False
  plot = ROOT.RooStats.LikelihoodIntervalPlot(intv)
  plot.nPoints = 50
  plot.Draw("")
  c.Update()
  c.SaveAs('prof_ll_calc.pdf')

#-------------------------------------------------------------------------------

def run_bayesian_calculator(mc, data):
  ## Prepare
  calc = ROOT.RooStats.BayesianCalculator(data, mc)
  calc.confidenceLevel = 0.683

  ## set the type of interval (not really needed for central which is the default)
  calc.leftSideTailFraction = 0.5 # for central interval
  # calc.leftSideTailFraction = 0. # for upper limit

  ## set the integration type (not really needed for the default ADAPTIVE)
  ## possible alternative values are  "VEGAS" , "MISER", or "PLAIN"  (MC integration from libMathMore) 
  ## "TOYMC" (toy MC integration, work when nuisances exist and they have a constraints pdf)
  itype = calc.integrationType = ""

  ## this is needed if using TOYMC
  if itype == "TOYMC":
    nuisPdf = ROOT.RooStats.MakeNuisancePdf(mc, "nuisance_pdf")
    if nuisPdf: 
      calc.ForceNuisancePdf(nuisPdf)

  ## compute interval by scanning the posterior function
  ## it is done by default when computing shortest intervals
  calc.scanOfPosterior = 100

  ## Calculate
  firstPOI = mc.parametersOfInterest.first();
  interval = calc.interval
  if not interval:
     print "Error computing Bayesian interval - exit "
     return

  ## draw plot of posterior function
  c = ROOT.TCanvas("BayesianCalculator")
  c.ownership = False
  calc.posteriorPlot.Draw()
  c.Update()
  c.SaveAs('bays_calc.pdf')

#-------------------------------------------------------------------------------

def run_hypothesis_test_inverter(w, data):
  ## Prepare
  sbModel = w.obj('sbModel')
  bModel  = w.obj('bModel')
  poi     = sbModel.parametersOfInterest.first()

  ## This is for the Asymptotic Calculator
  calc = ROOT.RooStats.AsymptoticCalculator(data, bModel, sbModel)
  calc.oneSided = True # for one-side tests (limits)
  calc.printLevel = 0

  ## We can now create the Inverter class
  useCLs = True
  invt = ROOT.RooStats.HypoTestInverter(calc)
  invt.confidenceLevel = 0.95
  invt.verbose = False
  invt.UseCLs(useCLs)

  ## We need also to configure the ToyMCSampler and set the test statistics
  toymcs = invt.hypoTestCalculator.testStatSampler
  # for number counting (extended pdf do not need this)
  toymcs.nEventsPerToy = 1
  # profile likelihood test statistics 
  profll = ROOT.RooStats.ProfileLikelihoodTestStat(sbModel.pdf)
  # for CLs (bounded intervals) use one-sided profile likelihood
  if useCLs: 
    profll.oneSided = True   
  # set the test statistic to use 
  toymcs.testStatistic = profll

  ## We can run now the inverter
  print "Doing a fixed scan in interval : {0.min}, {0.max}".format(poi)
  invt.fixedScan = 10, poi.min, poi.max
  r = invt.interval

  ## And finally we can query the result and make some plots:
  upperLimit = r.UpperLimit()
  ulError = r.UpperLimitEstimatedError()
  print "The computed upper limit is: {} +/- {}".format(upperLimit, ulError)
  
  ## compute expected limit
  print "Expected upper limits, using the B (alternate) model : "
  print " expected limit (median)", r.GetExpectedUpperLimit(0)
  print " expected limit (-1 sig)", r.GetExpectedUpperLimit(-1)
  print " expected limit (+1 sig)", r.GetExpectedUpperLimit(1)
  
  ## plot now the result of the scan 
  plot = ROOT.RooStats.HypoTestInverterPlot("HTI_Result_Plot", "Feldman-Cousins Interval", r)
  c = ROOT.TCanvas("HypoTestInverter Scan")
  c.ownership = False
  c.logy = False
  plot.Draw("CLb 2CL") # plot also CLb and CLs+b 
  c.Update()
  c.SaveAs('hypo_test_inverter.pdf')

#===============================================================================

if __name__ == '__main__':
  w, mc, data = prepare_workspace()
  run_profile_likelihood_calculator(mc, data)
  run_bayesian_calculator(mc, data)
  run_hypothesis_test_inverter(w, data)
  # raw_input()
