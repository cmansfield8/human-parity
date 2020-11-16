#!/bin/bash

# preprocessing steps
python src/preprocess_reference.py data/NIST2000 data SWBD
python src/preprocess_reference.py data/NIST2000 data CH
python src/preprocess_human.py data/human_parity data True
