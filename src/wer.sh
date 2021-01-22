#!/bin/bash

DATADIR=$1
OUT=$2

SCLITE="/home2/coman8/SCTK/bin/sclite"

$SCLITE -h ${DATADIR}/human.swb_processed.ctm ctm -r ${DATADIR}/SWBDO.stm stm -F -o all
$SCLITE -h ${DATADIR}/human.swb_processed.ctm ctm -r ${DATADIR}/SWBDO.stm stm -F -o sgml

$SCLITE -h ${DATADIR}/machine.swb_processed.ctm ctm -r ${DATADIR}/SWBDO.stm stm -F -o all
$SCLITE -h ${DATADIR}/machine.swb_processed.ctm ctm -r ${DATADIR}/SWBDO.stm stm -F -o sgml

$SCLITE -h ${DATADIR}/human.callhome_processed.ctm ctm -r ${DATADIR}/CHO.stm stm -F -o all
$SCLITE -h ${DATADIR}/human.callhome_processed.ctm ctm -r ${DATADIR}/CHO.stm stm -F -o sgml

$SCLITE -h ${DATADIR}/machine.callhome_processed.ctm ctm -r ${DATADIR}/CHO.stm stm -F -o all
$SCLITE -h ${DATADIR}/machine.callhome_processed.ctm ctm -r ${DATADIR}/CHO.stm stm -F -o sgml
