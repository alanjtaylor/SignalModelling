import ROOT
from ROOT import *
from array import array
import math
from optparse import OptionParser, OptionGroup, OptionValueError
import argparse
import os
import sys

RF = RooFit

gROOT.LoadMacro("/afs/cern.ch/work/a/altaylor/public/ATLASStyle/AtlasStyle.C")
gROOT.LoadMacro("/afs/cern.ch/work/a/altaylor/public/ATLASStyle/AtlasLabels.C")
gROOT.LoadMacro("/afs/cern.ch/work/a/altaylor/public/ATLASStyle/AtlasUtils.C")
gSystem.Load('RooTwoSidedCBShape/RooTwoSidedCBShape_cxx')

from ROOT import RooTwoSidedCBShape

if not os.path.exists("fitOutputs"):
    print 'making fitOutputs directory...'
    os.makedirs("fitOutputs")


SetAtlasStyle()
gROOT.SetBatch(kTRUE)

parser = argparse.ArgumentParser()

## take in the name of the process and the MC campaign
parser.add_argument('-n', '--name', action='store', required=True, help='Give name of sample (eg HH or can be allProc for all processes merged)')
parser.add_argument('-c', '--campaign', action='store', required=True, help='Give the MC campaign (eg mc16a or can be total)')
parser.add_argument('-v', '--variable', action='store', required=True, help='Give the variable to be fitted (eg myy or mjj)')
parser.add_argument('-f', '--function', action='store', required=True, help='Give the functional form, options include: DSCB, Chebychev, Exponential')
args = parser.parse_args()

listOfFunctions = [ "DSCB", "Bukin", "Chebychev", "Exponential", "Polynomial"]

if args.function not in listOfFunctions:
    sys.exit('Exiting, function specified is not in the list of functions specified...')

if args.variable == "myy" and args.function != "DSCB":
    sys.exit('Exiting, myy is only compatible with the DSCB function!')

if args.variable == "myy":
    
    myy_min = 113.0
    myy_max = 138.0
    n_bins = 25
    apdf = "RooTwoSidedCBShape::cb_C{0}("+args.variable+", muCB_C{0}[125,0.1,10000], sigmaCB_C{0}[1.7,0.01,200.0], alphaCBLo_C{0}[1.5,0.1,2.5], nCBLo_C{0}[9.0,0.1, 100.0], alphaCBHi_C{0}[2.2,0.1,3.0], nCBHi_C{0}[5.0, 0.1, 1000.0])"
    pdfname = "cb"
    x_axis_str = "M_{#gamma#gamma} [GeV]"
    y_axis_str = "Events / GeV"

if args.variable == "mjj":

    myy_min = 80.0
    myy_max = 180.0
    n_bins = 20
    x_axis_str = "M_{bb} [GeV]"
    y_axis_str = "Events / 5GeV" 

    ## the default is for DSCB with initial parameters suitable for HH 
    apdf = "RooTwoSidedCBShape::cb_C{0}("+args.variable+", muCB_C{0}[117,0.1,10000], sigmaCB_C{0}[18.0,0.01,200.0], alphaCBLo_C{0}[1.5,0.1,2.5], nCBLo_C{0}[9.0,0.1, 100.0], alphaCBHi_C{0}[2.2,0.1,3.0], nCBHi_C{0}[5.0, 0.1, 1000.0])"
    pdfname = "cb"

    if args.function == "Bukin" and args.name == "HH":
        ## suggested set up is to fix rho1
        apdf = "RooBukinPdf::bukin_C{0}("+args.variable+", peak_C{0}[125.0,50.0,200.0], width_C{0}[12.0,2.0,30.0], asymm_C{0}[1e-04,-1.0e+06,+1.0e+06],rho1_C{0}[-1e-05], rho2_C{0}[-1e-05,-1e+06,+1e+06])"
        pdfname = "bukin"

    if args.function == "Bukin" and (args.name == "ZH" or args.name == "ggZH" or args.name == "ZHMerge"):
        ## suggested set up is to fix rho1
        apdf = "RooBukinPdf::bukin_C{0}("+args.variable+", peak_C{0}[85.0,50.0,200.0], width_C{0}[12.0,2.0,30.0], asymm_C{0}[1e-04,-1.0e+06,+1.0e+06],rho1_C{0}[-1e-05], rho2_C{0}[-1e-05,-1e+06,+1e+06])"
        pdfname = "bukin"

    if args.function == "DSCB" and (args.name == "ZH" or args.name == "ggZH" or args.name == "ZHMerge"):
        apdf = "RooTwoSidedCBShape::cb_C{0}("+args.variable+", muCB_C{0}[80.0,70.0,130.0], sigmaCB_C{0}[20.0,0.01,200.0], alphaCBLo_C{0}[0.35], nCBLo_C{0}[9.0], alphaCBHi_C{0}[2.2,0.1,5.0], nCBHi_C{0}[5.0, 0.1, 1000.0])"
        pdfname = "cb"
        
    if args.function == "Chebychev":
        apdf = "Chebychev::cheb_C{0}("+args.variable+",{{a0_C{0}[0.0,-30.0,+30.0],a1_C{0}[0.0,-30.0,+30.0],a2_C{0}[0.0,-30.0,+30.0]}})"
        pdfname = "cheb"

    if args.function == "Polynomial":
        apdf = "Polynomial::poly_C{0}("+args.variable+",{{a0_C{0}[0.025,-30.0,+30.0],a1_C{0}[0.0,-30.0,+30.0],a2_C{0}[0.0,-30.0,+30.0]}})"
        pdfname = "poly"

    if args.function == "Exponential":
        apdf = "Exponential::expo_C{0}("+args.variable+",a0_C{0}[0.0,-30.0,+30.0])"
        pdfname = "expo"

ROOT.gStyle.SetPalette(1)
chain = TChain("CollectionTree")

inputFile = "skimmedFiles/"+args.name+"_"+args.campaign+".root"
chain.Add(inputFile)

afile = TFile(inputFile)
atree = afile.Get("CollectionTree")

m_yy = RooRealVar(args.variable, args.variable, myy_min, myy_max)

weight_var_str = "weight"
weight_var = RooRealVar(weight_var_str, weight_var_str, -1000.0, 1000.0)
cat_var_str = "catVariable"
cat_var = RooRealVar(cat_var_str, cat_var_str, -1000, 1000)

## find the min / max values of the categorisation variable
maxCatVal = int(chain.GetMaximum("catVariable"))
minCatVal = int(chain.GetMinimum("catVariable"))

varset = RooArgSet(m_yy, weight_var, cat_var)

# create workspace to hold the PDFs in
combWS = RooWorkspace("combWS","combWS")
getattr(combWS, 'import')(varset, RooCmdArg())

# create list of RooDataSets
dataList = [ ]
for j in range(minCatVal, maxCatVal+1):
    dataset = RooDataSet("data_C"+str(j),"data_C"+str(j), varset, RF.Import(chain), RF.WeightVar(weight_var), RF.Cut("catVariable == " + str(j)))
    dataList.append(dataset)


## keep a text file which has the final fit models
outputFile = open("fitOutputs/"+args.name+"_" + args.campaign + "_" + args.variable +"_fitModels.txt","w")
    

# loop over the datasets
for idx,data in enumerate(dataList):

    idy = idx+1
    combWS.factory(apdf.format(str(idy)))
    fitResult = combWS.pdf(pdfname+"_C"+str(idy)).fitTo(data,RF.Save(), RF.SumW2Error(True), RF.Range(myy_min, myy_max), RF.Minimizer("Minuit2", "migrad"))

    ## create simple histogram --> necessary for the ratio plot
    h_myy = TH1F("h_myy", "h_myy", n_bins, myy_min, myy_max )
    h_myy.Sumw2()
    var = args.variable
    sel = "(catVariable == " + str(idy)+")*weight"
    atree.Draw("%s >> h_myy" %var, "%s" %sel)
    h_myy.Draw()

    ## cosmetics 
    frame = combWS.var(args.variable).frame(myy_min , myy_max , n_bins )
    c1 = TCanvas("can", "can", 800, 800)
    pad1 = TPad( "pad1", "pad1", 0.00, 0.33, 1.00, 1.00 )
    pad2 = TPad( "pad2", "pad2", 0.00, 0.00, 1.00, 0.33 )
    pad1.SetBottomMargin(0.00001)
    pad1.SetBorderMode(0)
    pad2.SetTopMargin(0.00001)
    pad2.SetBottomMargin(0.4)
    pad2.SetBorderMode(0)
    c1.cd()
    pad1.Draw()
    pad2.Draw()
    pad1.cd()

    data.plotOn(frame)
    combWS.pdf(pdfname+"_C"+str(idy)).plotOn(frame, RF.LineColor(kRed) )
    frame.Draw()

    frame.SetMinimum(0.0)
    frame.GetYaxis().SetTitle(y_axis_str)

    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(kBlack)
    latex.SetTextSize(0.04)
    eventYield = "Yield =" + format( h_myy.Integral() , '.2f')

    if args.function == "DSCB":

        mu_CBVal = format( combWS.var("muCB_C"+str(idy)).getVal() , '.2f')
        sigma_CBVal = format( combWS.var("sigmaCB_C"+str(idy)).getVal() , '.2f')
        alpha_CBLoVal = format( combWS.var("alphaCBLo_C"+str(idy)).getVal() , '.2f')
        alpha_CBHiVal = format( combWS.var("alphaCBHi_C"+str(idy)).getVal() , '.2f')
        n_CBLoVal = format( combWS.var("nCBLo_C"+str(idy)).getVal() , '.2f')
        n_CBHiVal = format( combWS.var("nCBHi_C"+str(idy)).getVal() , '.2f')

        mu_CB = "#mu_{CB} =" + mu_CBVal + "#pm" + format( combWS.var("muCB_C"+str(idy)).getError() , '.2f')
        sigma_CB = "#sigma_{CB} =" + sigma_CBVal  + "#pm" + format( combWS.var("sigmaCB_C"+str(idy)).getError() , '.2f')
        alpha_CBLo = "#alpha_{CBLo} =" + alpha_CBLoVal  + "#pm" + format( combWS.var("alphaCBLo_C"+str(idy)).getError() , '.2f')
        alpha_CBHi = "#alpha_{CBHi} =" + alpha_CBHiVal  + "#pm" + format( combWS.var("alphaCBHi_C"+str(idy)).getError() , '.2f')
        n_CBLo = "n_{CBLo} =" + n_CBLoVal  + "#pm" + format( combWS.var("nCBLo_C"+str(idy)).getError() , '.2f')
        n_CBHi = "n_{CBHi} =" + n_CBHiVal  + "#pm" + format( combWS.var("nCBHi_C"+str(idy)).getError() , '.2f')

        latex.DrawLatex(0.7, 0.85 - 0.05, mu_CB)
        latex.DrawLatex(0.7, 0.85 - 0.1, sigma_CB)
        latex.DrawLatex(0.7, 0.85 - 0.15, alpha_CBLo)
        latex.DrawLatex(0.7, 0.85 - 0.20, alpha_CBHi)
        latex.DrawLatex(0.7, 0.85 - 0.25, n_CBLo)
        latex.DrawLatex(0.7, 0.85 - 0.30, n_CBHi)
        latex.DrawLatex(0.7, 0.85 - 0.35, eventYield)
        latex.DrawLatex(0.7, 0.85 - 0.40, args.name)
        latex.DrawLatex(0.7, 0.85 - 0.45, "C"+str(idy))

    if args.function == "Bukin":

        xpVal = format( combWS.var("peak_C"+str(idy)).getVal() , '.2f')
        widthVal = format( combWS.var("width_C"+str(idy)).getVal() , '.2f')
        asymmVal = format( combWS.var("asymm_C"+str(idy)).getVal() , '.2f')
        rhoOneVal = format( combWS.var("rho1_C"+str(idy)).getVal() , '.2f')
        rhoTwoVal = format( combWS.var("rho2_C"+str(idy)).getVal() , '.2f')

        xp = "x_{p} =" + xpVal + "#pm" + format( combWS.var("peak_C"+str(idy)).getError() , '.2f')
        widthA = "#sigma_{p} =" + widthVal  + "#pm" + format( combWS.var("width_C"+str(idy)).getError() , '.2f')
        asymm = "x_{i} =" + asymmVal  + "#pm" + format( combWS.var("asymm_C"+str(idy)).getError() , '.2f')
        rhoOne = "#rho_{1} =" + rhoOneVal  + "#pm" + format( combWS.var("rho1_C"+str(idy)).getError() , '.2f')
        rhoTwo = "#rho_{2} =" + rhoTwoVal  + "#pm" + format( combWS.var("rho2_C"+str(idy)).getError() , '.2f')

        
        latex.DrawLatex(0.7, 0.85 - 0.05, xp)
        latex.DrawLatex(0.7, 0.85 - 0.1, widthA)
        latex.DrawLatex(0.7, 0.85 - 0.15, asymm)
        latex.DrawLatex(0.7, 0.85 - 0.20, rhoOne)
        latex.DrawLatex(0.7, 0.85 - 0.25, rhoTwo)
        latex.DrawLatex(0.7, 0.85 - 0.30, eventYield)
        latex.DrawLatex(0.7, 0.85 - 0.34, args.name)
        latex.DrawLatex(0.7, 0.85 - 0.40, "C"+str(idy))


    if args.function == "Chebychev":

        a0Val = format( combWS.var("a0_C"+str(idy)).getVal() , '.2f')
        a1Val = format( combWS.var("a1_C"+str(idy)).getVal() , '.2f')
        a2Val = format( combWS.var("a2_C"+str(idy)).getVal() , '.2f')

        a0 = "a_{0} =" + a0Val  + "#pm" + format( combWS.var("a0_C"+str(idy)).getError() , '.2f')
        a1 = "a_{1} =" + a1Val  + "#pm" + format( combWS.var("a1_C"+str(idy)).getError() , '.2f')
        a2 = "a_{2} =" + a2Val  + "#pm" + format( combWS.var("a2_C"+str(idy)).getError() , '.2f')
        latex.DrawLatex(0.7, 0.85 - 0.05, a0)
        latex.DrawLatex(0.7, 0.85 - 0.10, a1)
        latex.DrawLatex(0.7, 0.85 - 0.15, a2)
        latex.DrawLatex(0.7, 0.85 - 0.20, args.name)
        latex.DrawLatex(0.7, 0.85 - 0.25, "C"+str(idy))

    if args.function == "Exponential":

        a0Val = format( combWS.var("a0_C"+str(idy)).getVal() , '.2f')
        
        a0 = "a_{0} =" + a0Val + "#pm" + format( combWS.var("a0_C"+str(idy)).getError() , '.2f')
        latex.DrawLatex(0.7, 0.85 - 0.15, a0)
        latex.DrawLatex(0.7, 0.85 - 0.20, args.name)
        latex.DrawLatex(0.7, 0.85 - 0.25, "C"+str(idy))
        
    
    pad2.cd()
    medianHist = TH1F("median", "median", n_bins, myy_min, myy_max );

    for x in range(1,n_bins+1):
        medianHist.SetBinContent(x,1.0)

    medianHist.SetLineColor(kRed)
    medianHist.SetLineWidth(2)
    medianHist.GetXaxis().SetTitle(x_axis_str)
    medianHist.GetYaxis().SetTitle("MC / Fit")

    medianHist.GetXaxis().SetTitleOffset(0.95)
    medianHist.GetYaxis().SetTitleOffset(0.7)
    medianHist.GetXaxis().SetTitleSize(0.1)
    medianHist.GetYaxis().SetTitleSize(0.1)
    medianHist.GetXaxis().SetLabelSize(0.1)
    medianHist.GetYaxis().SetLabelSize(0.1)
    medianHist.GetYaxis().SetRangeUser(-0.2, 2.2)
    medianHist.Draw()

    line = ROOT.TLine()
    line.SetLineStyle(1)
    line.SetLineWidth(2)
    line.SetLineColor(kRed)
    line.SetLineWidth(1)
    line.SetLineStyle(2)

    m_ratioMin = 0.0
    m_ratioMaxi = 2.0 

    line.DrawLine(myy_min,((1.0+m_ratioMin)/2.0),myy_max,((1.0+m_ratioMin)/2.0))
    line.DrawLine(myy_min,((1.0+m_ratioMaxi)/2.0),myy_max,((1.0+m_ratioMaxi)/2.0))

    n_events = data.sumEntries(args.variable + " > " + str(myy_min) +  " && " + args.variable + " < " + str(myy_max) )
    result = ROOT.TGraphErrors()
    increment = ( myy_max - myy_min ) / n_bins 
    combWS.var(args.variable).setRange("fullRange", myy_min, myy_max) 

    int_tot = combWS.pdf(pdfname + "_C"+str(idy)).createIntegral(  ROOT.RooArgSet( combWS.var(args.variable) ), RooFit.NormSet( ROOT.RooArgSet( combWS.var(args.variable) ) ), RooFit.Range("fullRange")  )
    val_tot = int_tot.getVal()
    pointIndex = 0
    pointIndexNonZero = 0
    
    result = TGraphErrors()
    i_m = myy_min

    chi2Prob = 0.0
    nDofs = 0
    
    while i_m < myy_max:

        combWS.var(args.variable).setRange("range_"+ str(i_m), i_m, ( i_m + increment ) )

        int_curr = combWS.pdf(pdfname+"_C"+str(idy)).createIntegral( ROOT.RooArgSet( combWS.var(args.variable) ), RooFit.NormSet( ROOT.RooArgSet( combWS.var(args.variable) ) ), RooFit.Range("range_"+ str(i_m))  )

        val_curr = int_curr.getVal()
        currMass = i_m + 0.5*increment
        curr_pdf_weight = n_events * ( val_curr / val_tot )
        var_name = combWS.var(args.variable).GetName()

        curr_data_weight = data.sumEntries( args.variable + " > " + str(i_m) + " && " + args.variable +" < " + str(i_m + increment) )
        curr_weight = curr_data_weight / curr_pdf_weight

        result.SetPoint(pointIndex,currMass, curr_weight)
        curr_error = h_myy.GetBinError(pointIndex+1) / curr_pdf_weight
        result.SetPointError(pointIndex, 0.0, curr_error)
        pointIndex += 1
        i_m += increment

    result.Draw("EPSAME")
    outputName = args.name+"_"+args.variable+"_"+args.campaign+"_"+"c"+str(idy)+".png"

    c1.SaveAs("fitOutputs/"+outputName)

    ## save the PDF to the workspace
    getattr(combWS,'import')(combWS.pdf(pdfname+"_C"+str(idy)))
    combWS.pdf(pdfname+"_C"+str(idy)).Print()

    strPDF = ""

    if args.function == "DSCB":

        strPDF = '"RooTwoSidedCBShape::'+args.name+'_cb_'+args.variable+'_C'+str(idy)+'('+args.variable+','+ args.name + '_muCB_C'+str(idy)+'['+mu_CBVal+'],'+ args.name + '_sigmaCB_C'+str(idy)+'['+sigma_CBVal+'],'
        strPDF += args.name + '_alphaCBLo_C'+str(idy)+'['+alpha_CBLoVal+'], ' + args.name + '_nCBLo_C'+str(idy)+'['+n_CBLoVal+'], ' + args.name + '_alphaCBHi_C'+str(idy)+'['+alpha_CBHiVal+'], ' + args.name + '_nCBHi_C'+str(idy)+'['+n_CBHiVal+'])"'

    if args.function == "Chebychev":
        strPDF = '"Chebychev::'+args.name+'_cheb_'+args.variable+'_C'+str(idy)+'('+args.variable+','+'a0_C'+str(idy)+'['+a0Val+'],'+'a1_C'+str(idy)+'['+a1Val+'],'+'a2_C'+str(idy)+'['+ a2Val +'])"'

    if args.function == "Exponential":
        strPDF = '"Exponential::' + args.name + '_expo_' + args.variable + '_C' + str(idy) + '(' + args.variable +',a0_C'+str(idy)+'['+a0Val+'])"'

    outputFile.write(strPDF+"\n")
    
    del h_myy
    del medianHist

combWS.writeToFile("fitOutputs/"+args.name+"_" + args.campaign + "_" + args.variable +"_WS.root",True)
outputFile.close()
