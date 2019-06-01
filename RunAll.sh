#!/bin/bash
# write out HH files separately - this is due to the HH files on the HGam EOS space being bugged.
echo 'Opted to skim all the HH + single Higgs files.. this takes about 10mins'
python skimFiles.py -p HH -c mc16a
python skimFiles.py -p HH -c mc16d
python skimFiles.py -p HH -c mc16e
hadd skimmedFiles/HH_total.root skimmedFiles/HH_mc16?.root

for process in ggH VBF WpH WmH ZH ggZH ttH bbH tWH tHjb; do
    for mc in a d e; do 
	python skimFiles.py -p ${process} -c mc16${mc}
    done
    # for each process, merge the MC campaigns together
    hadd skimmedFiles/${process}_total.root skimmedFiles/${process}_mc16?.root
done
# create a file with all samples merged together
echo 'Create file allProc_total.root with all processes and MC campaigns merged together' 
hadd skimmedFiles/allProc_total.root skimmedFiles/*_total.root
echo 'Create file with ZH and ggZH merged together'
hadd skimmedFiles/ZHMerge_total.root skimmedFiles/ZH_total.root skimmedFiles/ggZH_total.root

