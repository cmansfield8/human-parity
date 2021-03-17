#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" utils.py
Author: coman8@uw.edu

Utiltiy functions and classes for the project.
"""

import sys
import os
import csv
import re
import pandas as pd


class Counter:

    def __init__(self):
        self.ix = 0
        self.hyp = 0
        self.ref = 0
        self.hyp_cont = 0
        self.ref_cont = 0

    def iterall(self, atype):
        self.ix += 1
        if atype != 'D':
            self.hyp += 1
            self.hyp_cont += 1
        if atype != 'I':
            self.ref += 1
            self.ref_cont += 1

    def iter(self, source=None):
        if source == "ref_cont":
            self.ref_cont += 1
        elif source == "hyp_cont":
            self.hyp_cont += 1

    def itercont(self, row, atype):
        try:
            if atype != 'D' and row['hyp_cont_tag_gloss'][self.hyp_cont] == 1:
                self.iter('hyp_cont')
            if atype != 'I' and row['ref_cont_tag_gloss'][self.ref_cont] == 1:
                self.iter('ref_cont')
        except IndexError:
            catch_index_error(row, vars(self))
            raise


def load_file(projdir, file):
    infile = os.path.join(projdir, file)
    print('Loading {}'.format(infile))
    df = pd.read_csv(infile, index_col=0)
    return df

def write_file(errors, projdir, file, cols=None):
    output = os.path.join(projdir, file)
    print('Writing to {}'.format(output))
    with open(output, 'w', encoding='utf-8') as out:
        writer = csv.writer(out, lineterminator='\n')
        if cols:
            writer.writerow(cols)
        for e in errors:
            writer.writerow(e.get_data())


def ix_name(ix, i):
    ix_name = re.sub(r"\((.+)\)", r"\1", ix)
    ix_name = ix_name + "#" + str(i)
    return ix_name


def catch_index_error(*args):
    print('IndexError')
    for a in args:
        print(a)
    print(sys.exc_info()[0])
