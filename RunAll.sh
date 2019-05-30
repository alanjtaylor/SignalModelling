#!/bin/bash
# write out HH files separately - this is due to the HH files on the HGam EOS space being bugged.
echo 'Opted to skim all the HH + single Higgs files.. this takes about 10mins'
python skimFiles.py -s HH -c mc16a -p 0
python skimFiles.py -s HH -c mc16d -p 0
python skimFiles.py -s HH -c mc16e -p 0

hadd skimmedFiles/HH_total.root skimmedFiles/HH_mc16?.root

for sample in ggH VBF WpH WmH ZH ggZH ttH bbH tWH tHjb; do
    for mc in a d e; do 
	python skimFiles.py -s ${sample} -c mc16${mc} -p 1
    done
    # for each process, merge the MC campaigns together
    hadd skimmedFiles/${sample}_total.root skimmedFiles/${sample}_mc16?.root
done
# create a file with all samples merged together
echo 'Create file allProc_total.root with all processes and MC campaigns merged together' 
hadd skimmedFiles/allProc_total.root skimmedFiles/*_total.root
echo 'Create file with ZH and ggZH merged together'
hadd skimmedFiles/ZHMerge_total.root skimmedFiles/ZH_total.root skimmedFiles/ggZH_total.root

