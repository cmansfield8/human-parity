#!/bin/bash

DATADIR=$1 # parent of model dir

# extract utterances - from sclite sgml files
python src/get_utterance_table.py ${DATADIR}

# get full csv - when models are complete (.uni, .gru, and .tag csv in models directory)
src/gather.sh ${DATADIR}

# get (single token) errors
python src/get_error_table.py ${DATADIR}

# get frequency statistics
python src/misc/token_freq_stats.py ${DATADIR}/models > "${DATADIR}/freq_stats.txt" --top 50

# get disf. frequency
python src/misc/token_freq_stats.py ${DATADIR}/models --disf 1 > "${DATADIR}/hbkac_stats.txt"
