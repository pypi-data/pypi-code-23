#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyroot_zen import ROOT
ROOT.gROOT.batch = True

## Raw data (originally using pandas.DataFrame)
ZLL_THEO_CSC = {
  # PDF        nominal   stat        pdf+      pdf- (68%CL)
  'ABM12'  : ( 93.9673 , 0.0664061 , 1.13218 , 1.13218 ),
  'CT10'   : ( 94.252  , 0.0821569 , 3.56697 , 3.59106 ),
  'CT14'   : ( 93.9498 , 0.107521  , 2.5019  , 2.1011  ),
  'HERA15' : ( 97.3904 , 0.0804132 , 1.39495 , 1.39495 ),
  'MMHT14' : ( 94.8812 , 0.0919579 , 1.97459 , 1.94782 ),
  'MSTW08' : ( 94.7139 , 0.0819357 , 1.97321 , 1.76943 ),
  'NNPDF30': ( 92.6211 , 0.109097  , 2.0747  , 2.0747  ),
}

LHCb_FONT_FIXED = 133
LHCb_SIZE_FIXED = 20

def sum_quadratic(l1, l2):
  """
  Helper adapter to pair-wise quadratic-sum from 2 given lists.
  """
  return [(v1**2+v2**2)**0.5 for v1,v2 in zip(l1,l2)]

def adapter_asym(values, errors_high, errors_low):
  """
  Helper adapters for TGraphAsymmerrors.
  """
  n = len(values)
  return n, values, range(n,0,-1), errors_low, errors_high, [0.]*n, [0.]*n


def main():
  ## Unpack 
  labels, raws = zip(*sorted(ZLL_THEO_CSC.items()))
  vals, stats, pdfh, pdfl = zip(*raws)
  errsh = sum_quadratic(stats, pdfh)
  errsl = sum_quadratic(stats, pdfl)

  ## Prepare canvas
  c = ROOT.TCanvas('csc', 'Zll 8TeV cross-sections', 800, 600)
  c.ownership = False

  ## All errors, draw as back-grey
  g1 = ROOT.TGraphAsymmErrors(*adapter_asym(vals, errsh, errsl))
  g1.ownership      = False
  g1.lineColorAlpha = 1, 0.5

  ## Statistical uncertainty, draw as fore-black
  g2 = ROOT.TGraphAsymmErrors(*adapter_asym(vals, stats, stats))
  g2.ownership    = False
  g2.markerStyle  = 8
  g2.markerSize   = 0.5

  ## Putting them together
  g = ROOT.TMultiGraph()
  g.ownership = False
  g.Add(g1, 'AP')
  g.Add(g2, 'AP')
  g.Draw('A')

  ## shared axis limit
  limits = 94-5, 94+5

  ## Tune the multigraph
  g.minimum           = 0
  g.maximum           = len(labels)+2
  g.xaxis.limits      = limits
  g.xaxis.title       = '#sigma(pp #rightarrow Z) [pb]'
  g.xaxis.labelFont   = LHCb_FONT_FIXED
  g.xaxis.labelSize   = LHCb_SIZE_FIXED
  g.xaxis.titleFont   = LHCb_FONT_FIXED
  g.xaxis.titleSize   = LHCb_SIZE_FIXED * 1.2
  g.xaxis.titleOffset = 1.0
  g.yaxis.tickSize    = 0
  g.yaxis.labelSize   = 0

  ## Y-labels
  t = ROOT.TPaveText(0.02, 0.15, 0.3, 0.845, 'NDC')
  t.ownership       = False
  t.fillColorAlpha  = 0, 0.
  t.textFont        = LHCb_FONT_FIXED
  t.textSize        = LHCb_SIZE_FIXED
  t.textAlign       = 12
  for lab in labels:
    t.AddText(lab)
  t.Draw('NB')

  ## Legend
  leg = ROOT.TLegend(0.86, 0.85, 0.98, 0.97)
  leg.AddEntry(g1, 'Data_{stat}', 'f')
  leg.AddEntry(g2, 'Data_{tot}' , 'f')
  leg.borderSize = 0
  leg.textAlign  = 32
  leg.Draw()

  ## Description
  text2 = ROOT.TPaveText(0.04, 0.92, 0.20, 0.97, 'NDC')
  text2.AddText('LHCb, #sqrt{s} = 8 TeV, 2 fb^{-1}')
  text2.textFont  = LHCb_FONT_FIXED
  text2.textSize  = LHCb_SIZE_FIXED * 1.2
  text2.fillColor = 0
  text2.textAlign = 12
  text2.Draw('NB')

  ## Acceptance
  text3 = ROOT.TPaveText(0.76, 0.14, 0.98, 0.35, 'NDC')
  text3.AddText('#font[12]{l} = #font[12]{e, #mu, #tau}')
  text3.AddText('#font[12]{p}_{T}^{#font[12]{l}} > 20 GeV/#font[12]{c}')
  text3.AddText('2.0 < #eta^{#font[12]{l}} < 4.5')
  text3.AddText('60 < #font[12]{M}_{#font[12]{ll}} < 120 GeV/#font[12]{c}^{2}')
  text3.textFont  = LHCb_FONT_FIXED
  text3.textSize  = LHCb_SIZE_FIXED
  text3.textAlign = 32
  text3.fillColor = 0
  text3.Draw('NB')

  ## Finally
  c.RedrawAxis()
  c.topMargin    = 0.01
  c.leftMargin   = 0.02
  c.bottomMargin = 0.10
  c.rightMargin  = 0.01
  c.Update()
  c.SaveAs('lhcb_z_csc.pdf')

if __name__ == '__main__':
  main()
