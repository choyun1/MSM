#!/bin/bash
pdfjam /home/acho/Sync/KiddLab/MSM/notebooks/analysis/results.pdf /home/acho/Sync/KiddLab/MSM/notebooks/analysis/data_pilot_v5.pdf --nup 2x1 --delta '-135 0' --landscape --outfile /home/acho/Sync/KiddLab/MSM/notebooks/analysis/combined.pdf
pdf-crop-margins -v -p 0 -a -6 combined.pdf
rm -f combined.pdf
mv combined_cropped.pdf combined.pdf
