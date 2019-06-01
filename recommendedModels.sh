#!/bin/bash
python SignalModel.py -p HH -c total -v myy -f DSCB
python SignalModel.py -p allProc -c total -v myy -f DSCB
python SignalModel.py -p HH -c total -v mjj -f DSCB
python SignalModel.py -p HH -c total -v mjj -f Bukin
python SignalModel.py -p ZHMerge -c total -v mjj -f DSCB
python SignalModel.py -p ZHMerge -c total -v mjj -f Bukin
python SignalModel.py -p ttH -c total -v mjj -f Chebychev
