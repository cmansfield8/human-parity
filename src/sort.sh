#!/bin/bash

IN=$1
OUT=$2

sort +0 -1 +1 -2 +3nb -4 $IN > $OUT
