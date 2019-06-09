import ROOT
from ROOT import *
from array import array
import math
from optparse import OptionParser, OptionGroup, OptionValueError
import argparse
import os
import sys
import re

RF = RooFit

gROOT.LoadMacro("/afs/cern.ch/work/a/altaylor/public/ATLASStyle/AtlasStyle.C")
gROOT.LoadMacro("/afs/cern.ch/work/a/altaylor/public/ATLASStyle/AtlasLabels.C")
gROOT.LoadMacro("/afs/cern.ch/work/a/altaylor/public/ATLASStyle/AtlasUtils.C")
gSystem.Load('RooTwoSidedCBShape/RooTwoSidedCBShape_cxx')

from ROOT import RooTwoSidedCBShape
SetAtlasStyle()
ROOT.gROOT.SetBatch(kTRUE)

## use a nice custom palette

NRGBs = 5
NCont = 255
stops = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
red = [ 0.00, 0.00, 0.87, 1.00, 0.51 ]
green = [ 0.00, 0.81, 1.00, 0.20, 0.00 ]
blue = [ 0.51, 1.00, 0.12, 0.00, 0.00 ]
stopsArray = array('d', stops)
redArray   = array('d', red)
greenArray = array('d', green)
blueArray  = array('d', blue)
TColor.CreateGradientColorTable(NRGBs, stopsArray, redArray, greenArray, blueArray, NCont)
ROOT.gStyle.SetNumberContours(NCont)

if not os.path.exists("correlations"):
    print 'making correlations directory...'
    os.makedirs("correlations")

parser = argparse.ArgumentParser()
parser.add_argument('-p_mjj', '--process_mjj', action='store', required=True, help='Give name of di-jet PDF model to be used (eg HH or can be allProc for all processes merged)')
parser.add_argument('-p_myy', '--process_myy', action='store', required=True, help='Give name of di-photon PDF model to be used (eg HH or can be allProc for all processes merged)')
parser.add_argument('-f', '--function', action='store', required=True, help='Give the functional form, options include: DSCB, Chebychev, Exponential')
args = parser.parse_args()

listOfFunctions = [ "DSCB", "Bukin", "Chebychev", "Exponential"]

if args.function not in listOfFunctions:
    sys.exit('Exiting, function specified is not in the list of functions specified...')

## logscale for the z-axis
c1 = TCanvas()
c1.SetLogz()

mjjPDFs = open('fitOutputs/'+args.process_mjj+'_total_mjj_'+args.function+'_fitModels.txt','r').readlines()
myyPDFs = open('fitOutputs/'+args.process_myy+'_total_myy_DSCB_fitModels.txt','r').readlines()

## create a 2D histogram from the best fit PDFs.
myy_min = 118.0
myy_max = 132.0

# entries per 0.5gev 
n_bins_yy = 28

# entries per 5gev 
mjj_min = 80.0
mjj_max = 180.0
n_bins_jj = 20

myy = ROOT.RooRealVar("myy", "myy", myy_min, myy_max)
mjj = ROOT.RooRealVar("mjj", "mjj", mjj_min, mjj_max)

varset_myy = ROOT.RooArgSet(myy)
varset_mjj = ROOT.RooArgSet(mjj)

combWS = ROOT.RooWorkspace("myws","myws")

getattr(combWS, 'import')(varset_myy, ROOT.RooCmdArg())
getattr(combWS, 'import')(varset_mjj, ROOT.RooCmdArg())

## open the MC
afile = TFile("skimmedFiles/"+args.process_mjj+"_total.root")
atree = afile.Get("CollectionTree")

# m_[bb] : m_[yy] 
var = "mjj:myy"

for i,line in enumerate(myyPDFs):

    idy = i+1

    ## construct the 2D MC histogram

    h_mjj_myyMC = TH2F("h_mjj_myyMC_"+str(idy), "h_mjj_myyMC_"+str(idy), n_bins_yy, myy_min, myy_max, n_bins_jj, mjj_min, mjj_max )
    h_mjj_myyMC.Sumw2()

    histo_str = "%s >> h_mjj_myyMC_"+str(idy)
    sel = "(catVariable == " + str(idy) + ")*weight"
    atree.Draw(histo_str %var, "%s" %sel)
    normFactor = h_mjj_myyMC.Integral()

    ## construct a histogram from the PDFs 
    ## strip the "" from the PDFs
    myyPart = myyPDFs[i][1:-2]
    mjjPart = mjjPDFs[i][1:-2]
    
    myyPDFname = re.search('(?<=::)\w+', myyPDFs[i])
    mjjPDFname = re.search('(?<=::)\w+', mjjPDFs[i])

    myyNAME = myyPDFname.group(0)
    mjjNAME = mjjPDFname.group(0)

    combWS.factory(myyPart)
    combWS.factory(mjjPart)
    combWS.factory("PROD::myy_mjj_PDF_C"+str(idy)+"("+myyNAME+", "+mjjNAME+")")

    apdf = combWS.pdf("myy_mjj_PDF_C"+str(idy))
    h_mjj_myyPDF = apdf.createHistogram("h_mjj_myyPDF_C"+str(idy),combWS.var("myy") , RF.Binning(n_bins_yy), RF.YVar(combWS.var("mjj") ,RF.Binning(n_bins_jj) ))
    h_mjj_myyPDF.Scale(normFactor)

    y_label = 0.88
    t = TLatex()
    t.SetTextAngle(90)
    t.SetNDC()
    c1.SetRightMargin(0.18)
    c1.SetLeftMargin(0.15)

    h_mjj_myyMC.GetYaxis().SetTitle("m_{bb} [GeV]")
    h_mjj_myyMC.GetXaxis().SetTitle("m_{\gamma\gamma} [GeV]")
    h_mjj_myyMC.GetZaxis().SetTitle("")

    h_mjj_myyPDF.GetYaxis().SetTitle("m_{bb} [GeV]")
    h_mjj_myyPDF.GetXaxis().SetTitle("m_{\gamma\gamma} [GeV]")
    h_mjj_myyPDF.GetZaxis().SetTitle("")

    h_mjj_myyMC.GetZaxis().SetRangeUser(0.000001,0.1)
    h_mjj_myyPDF.GetZaxis().SetRangeUser(0.000001,0.1)

    h_mjj_myyMC.Draw("COLZ")
    c1.SaveAs("correlations/"+args.process_mjj+"_MCHisto_C"+str(idy)+".png")

    h_mjj_myyPDF.Draw("COLZ")

    c1.SaveAs("correlations/"+args.process_mjj+"_PDFHisto_C"+str(idy)+".png")

    ## find the residual between the 2D histogram and the 2D MC PDF
    h_residual = TH2F("h_residual", "h_residual", n_bins_yy, myy_min, myy_max, n_bins_jj, mjj_min, mjj_max )

    h_residual.GetYaxis().SetTitle("m_{bb} [GeV]")
    h_residual.GetXaxis().SetTitle("m_{\gamma\gamma} [GeV]")
    h_residual.GetZaxis().SetTitle("")

    
    for i in range(1,h_mjj_myyMC.GetXaxis().GetNbins()+1):
        for j in range(1,h_mjj_myyMC.GetYaxis().GetNbins()+1):

            mc_stat_error = h_mjj_myyMC.GetBinError(i,j)

            if mc_stat_error != 0.0:
                
                residual = ( h_mjj_myyMC.GetBinContent(i,j) - h_mjj_myyPDF.GetBinContent(i,j) ) / mc_stat_error
                h_residual.SetBinContent(i,j,residual)

    h_residual.Draw("COLZ")
    c1.SaveAs("correlations/"+args.process_mjj+"_ResidualHisto_C"+str(idy)+".png")

    del h_residual
