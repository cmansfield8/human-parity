#!/bin/bash

DATADIR=$1

MODIR=$DATADIR/models

# add quotes to lists

gsed -i 's/^/"/' ${MODIR}/*.uni
gsed -i 's/$/"/' ${MODIR}/*.uni

gsed -i 's/^/"/' ${MODIR}/*.gru
gsed -i 's/$/"/' ${MODIR}/*.gru

declare -a names=("human.swb" "machine.swb" "human.callhome" "machine.callhome")

for i in "${names[@]}"
do
	# generate transcript-specific file
	PREFIX=${i}_processed
  MFILE=${MODIR}/${PREFIX}
	
	echo "Creating file ${MFILE}.all"
	cp ${DATADIR}/${PREFIX}.ctm.csv ${MFILE}.all

	for STYPE in hyp ref
	do
		# add related lm scripts, fixing the column names as we go
		SFILE=${MFILE}_${STYPE}
		
		gsed -i "1s/,/,${STYPE}_/g" ${SFILE}.tag
		gsed -i "1s/^/${STYPE}_/" ${SFILE}.tag
		paste -d "," ${MFILE}.all ${SFILE}.tag > ${MFILE}.tmp && mv ${MFILE}.tmp ${MFILE}.all

		gsed -i "1i ${STYPE}_prob" ${SFILE}.uni
		paste -d "," ${MFILE}.all ${SFILE}.uni > ${MFILE}.tmp && mv ${MFILE}.tmp ${MFILE}.all

		gsed -i "1i ${STYPE}_cprob" ${SFILE}.gru
		paste -d "," ${MFILE}.all ${SFILE}.gru > ${MFILE}.tmp && mv ${MFILE}.tmp ${MFILE}.all
	done
done
