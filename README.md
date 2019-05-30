# Signal Modelling
Tool for fitting analytical PDFs.

Instructions for lxplus.cern.ch:

. setup.sh

root -l -q RooTwoSidedCBShape.cxx+

The skimFiles.py script skims MxAODs into small ntuples using RDataFrame. The usage is:

python skimFiles.py -s eg. HH -c eg. mc16a -d eg. 0

or you can run over all samples and all MC campaigns with:

. RunAll.sh

The output files will finish in a directory /skimmedFiles.

To fit the PDFs:

python SignalModel.py -s HH -c total -v mjj -f Bukin

It is also possible to run over merged samples - allProc_total.root is all samples and MC campaigns merged together and ZHMerge is ggZH and qqZH merged together. 

The output fitted models will be available in the directory /fitOutputs.

