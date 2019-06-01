import yaml
import ROOT
import os

from optparse import OptionParser, OptionGroup, OptionValueError
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--process', action='store', required=True, help='Give name of process (eg ttH)')
parser.add_argument('-c', '--campaign', action='store', required=True, help='Give the MC campaign (eg mc16a)')
args = parser.parse_args()

print 'Creating RDF for process ', args.process, ' and for MC campaign ' , args.campaign

configFile = yaml.safe_load(open('files.yaml'))

treeName = "CollectionTree"

## take the MC campaign from the command line

lumi = configFile[args.campaign+"_lumi"]

fileName = configFile["Files"][args.process][args.campaign]

# at present, the HH and the single Higgs processs are kept at different directories due to the HH signal processes being bugged on the HGam EOS space 
if args.process != "HH":
    fileName = configFile["EOSPrefix"] + args.campaign + "/Nominal/" + fileName
    
histoName = configFile["Files"][args.process]["histogram"]

## get histogram from file for normalisation

aFile = ROOT.TFile(fileName)
sumWeights = (  aFile.Get(histoName).GetBinContent(1) / aFile.Get(histoName).GetBinContent(2) )*aFile.Get(histoName).GetBinContent(3)
scaleFactor = lumi / sumWeights

# create RDF
RDF = ROOT.ROOT.RDataFrame
d = RDF(treeName, fileName)

# filter the dataframe with the cuts
d_cut = d.Filter(configFile["Cuts"])

# can add more variables with a loop in future
dOut = d_cut.Define(configFile["Variables"][0][0], configFile["Variables"][0][1]) \
.Define(configFile["Variables"][1][0], configFile["Variables"][1][1]).Define(configFile["Variables"][2][0], configFile["Variables"][2][1]) \
.Define(configFile["Variables"][3][0], configFile["Variables"][3][1]+"*"+str(scaleFactor))

if not os.path.exists("skimmedFiles"):
    print 'making skimmedFiles directory...'
    os.makedirs("skimmedFiles")

outFileName = "skimmedFiles/"+args.process+"_"+args.campaign+".root"
branchList = ROOT.vector('string')()

for j in configFile["Variables"]:
    branchList.push_back(configFile["Variables"][j][0])

dOut.Snapshot(treeName, outFileName, branchList)
