#!/bin/bash

DATADIR=$1

# extract utterances
python src/get_utterance_table.py ${DATADIR}

# get (single token) errors
python src/get_error_table.py ${DATADIR}

# get frequency statistics
python src/misc/token_freq_stats.py ${DATADIR} > "${DATADIR}/freq_stats.txt"
