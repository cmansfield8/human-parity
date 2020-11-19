#!/bin/bash

# preprocessing steps
python src/preprocess_ref.py data/NIST2000 data SWBD
python src/preprocess_ref.py data/NIST2000 data CH
python src/preprocess_hyp.py data/human_parity data
sort +0 -1 +1 -2 +3nb -4 data/CH.stm > data/CHO.stm
rm data/CH.stm
sort +0 -1 +1 -2 +3nb -4 data/SWBD.stm > data/SWBDO.stm
rm data/SWBD.stm