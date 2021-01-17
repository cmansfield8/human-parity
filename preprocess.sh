#!/bin/bash

DATADIR=$1

# preprocessing steps before running SCLITE scoring program

python src/preprocess_ref.py data/NIST2000 $DATADIR SWBD --cont
python src/preprocess_ref.py data/NIST2000 $DATADIR CH --cont
python src/preprocess_hyp.py data/human_parity $DATADIR
sort +0 -1 +1 -2 +3nb -4 ${DATADIR}/CH.stm > ${DATADIR}/CHO.stm
rm ${DATADIR}/CH.stm
sort +0 -1 +1 -2 +3nb -4 ${DATADIR}/SWBD.stm > ${DATADIR}/SWBDO.stm
rm ${DATADIR}/SWBD.stm

