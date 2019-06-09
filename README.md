# Signal Modelling
Tool for fitting analytical PDFs.

## How to setup

    source setup.sh
    
    root -l -q RooTwoSidedCBShape/RooTwoSidedCBShape.cxx+ (first time only)
  
## How to run the code

The skimFiles.py script skims MxAODs into small ntuples using RDataFrame. The usage is:

```
python skimFiles.py -p HH -c mc16a
```

where p is the process to be run over and c is the MC campaign. The above is an example (HH and mc16a). All files are listed in `files.yaml`. Additional samples can be easily added. The selections used to skim the MxAOD is specified in `files.yaml` and can be easily modified. It is essential to have a "categorisation variable" in the MxAODs.  

You can also run over all processes and MC campaigns with:

    . RunAll.sh

In both cases, the output will create a new folder `skimmedFiles` which will contain the tiny ntuple(s) with only the variables listed in `files.yaml`. An ntuple is produced for each process and MC campaign. In the case of the `RunAll.sh` script, it will also produce additional files:

* `allProc_total.root`: contains all processes and all MC campaigns merged together in a single file. 
* `{process}_total.root`: contains all MC campaigns merged together for a single process. 
* `ZHMerge_total.root`: contains the ZH and ggZH processes and all MC campaigns merged together in a single file. 


To fit the PDFs:
    
    python SignalModel.py -p HH -c mc16a -v myy -f DSCB

where p is the process (can also be allProc or ZHMerge), c is the MC campaign (can also be total where all campaigns are merged together), v is the variable to be fitted (only myy or mjj for now) and f is the PDF to be used (DSCB, Bukin, Chebychev and Exponential for now). There is also the `recommendedModels.sh` script that will fit a recommended PDF for each process and variable.  

The output will create a folder `fitOutputs`. Here, a .png of each fit is produced, a .txt file which has the fitted PDFs written out and a .root file which contains a RooWorkspace with the fitted PDFs.

Once the fits have been performed it is possible to check if the product of the 1D PDFs can model the full 2D PDF. The residual 2D histograms can be plotted with

    python getResidual2D.py -p_mjj HH -p_myy allProc -f DSCB

where p_mjj is the process used for the di-jet mass fit and p_myy is the process(es) for the diphoton mass fit. The function used for the di-jet mass fit must also be specified with -f. The residuals for the recommended models can be run with the getAllResiduals2D.sh script. 

