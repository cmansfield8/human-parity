#!/bin/bash

# preprocessing steps
python src/preprocess_ref.py data/NIST2000 data SWBD
python src/preprocess_ref.py data/NIST2000 data CH
python src/preprocess_hyp.py data/human_parity data
