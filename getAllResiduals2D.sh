#!/bin/bash
python getResidual2D.py -p_mjj HH -p_myy allProc -f DSCB
python getResidual2D.py -p_mjj ZHMerge -p_myy allProc -f DSCB 
python getResidual2D.py -p_mjj ttH -p_myy allProc -f Chebychev
python getResidual2D.py -p_mjj ggH -p_myy allProc -f Exponential

