#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" get_error_table.py
Author: coman8@uw.edu

Given the csv of model infos, generates a csv of error info only.
"""

import argparse
import sys
import os
import csv
import re
from ast import literal_eval
import pandas as pd


class SError:

    def __init__(self, token='', pos='', shape='',
                 prob='', cprob=''):
        self.token = token
        self.pos = pos
        self.shape = shape
        self.prob = prob
        self.cprob = cprob

    @staticmethod
    def get_columns(stype='unk'):
        c = ['token', 'pos', 'shape', 'prob', 'cprob']
        return [stype + '_' + x for x in c]

    def get_data(self):
        d = [self.token, self.pos, self.shape, self.prob, self.cprob]
        return [str(x) for x in d]

class TError:

    def __init__(self, ix, annotation=None, position=None,
                 sen_len=None, ref=SError(), hyp=SError()):
        self.ix = ix
        self.annotation = annotation
        self.position = position
        self.sen_len = sen_len
        self.ref = ref
        self.hyp = hyp

    @staticmethod
    def get_columns():
        c = ['ix', 'annotation', 'position', 'sen_len', 'ref', 'hyp']
        c.extend(SError.get_columns('hyp'))
        c.extend(SError.get_columns('ref'))
        return c

    def get_data(self):
        d = [self.ix, self.annotation, self.position, self.sen_len]
        d.extend(self.hyp.get_data())
        d.extend(self.ref.get_data())
        return [str(x) for x in d]


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


class Main:
    ERRORS = ['I', 'D', 'S']

    def __init__(self, projdir):
        for file in os.listdir(projdir):
            if file.endswith('.all'):
                # load file
                infile = os.path.join(projdir, file)
                print('Loading {}'.format(infile))
                df = pd.read_csv(infile, index_col=0)

                errors = self.get_errors(df)

                # write file
                output = file[:-4] + '_errors.csv'
                output = os.path.join(projdir, output)
                print('Writing to {}'.format(output))
                with open(output, 'w', encoding='utf-8') as out:
                    writer = csv.writer(out, lineterminator='\n')
                    writer.writerow(TError.get_columns())
                    for e in errors:
                        writer.writerow(e.get_data())

    def get_errors(self, df):
        # read columns as list
        columns = df.columns[8:]
        for c in columns:
            df[c] = df[c].apply(lambda x: literal_eval(x))

        # get errors from each sentence
        result = list()
        for ix, row in df.iterrows():
            temp = self.extract_errors(ix, row)  # list errors
            if temp:
                result.extend(temp)

        return result

    def extract_errors(self, ix, row):
        errors = list()
        i = Counter()
        ann = row['annotation']

        for j in range(len(ann)):
            try:
                atype = ann[j]
            except IndexError:
                self.catch_index_error(ann, j)
                raise

            # since TAG has tokenized contractions, skip those
            try:
                if atype != 'D' and row['hyp_cont_tag_gloss'][i.hyp_cont] == 1:
                    i.iter('hyp_cont')
                if atype != 'I' and row['ref_cont_tag_gloss'][i.ref_cont] == 1:
                    i.iter('ref_cont')
            except IndexError:
                self.catch_index_error(row, vars(i))
                raise

            if atype in self.ERRORS:
                ix_name = re.sub(r"\((.+)\)", r"\1", ix)
                ix_name = ix_name + "#" + str(j)
                e = TError(ix_name)

                # source-specific information
                e.annotation = atype
                if atype != 'D':
                    e.hyp = self.extract_src(row, i, label='hyp')
                if atype != 'I':
                    e.ref = self.extract_src(row, i, label='ref')

                # position info
                e.position = i.ref + 1
                e.sen_len = len([x for x in ann if x != 'I'])

                errors.append(e)
            i.iterall(atype)
        return errors

    def extract_src(self, row, i, label=None):
        if label == 'hyp':
            count = i.hyp
            ccount = i.hyp_cont
        if label == 'ref':
            count = i.ref
            ccount = i.ref_cont

        se = SError()
        try:
            se.token = row[label + '_sent'][i.ix]
            se.pos = row[label + '_tag'][ccount]
            se.shape = row[label + '_shape'][ccount]
            se.prob = row[label + '_prob'][count]
            se.cprob = row[label + '_cprob'][count]
        except IndexError:
            self.catch_index_error(row, vars(i))
        return se

    def catch_index_error(*args):
        print('IndexError')
        for a in args:
            print(a)
        print(sys.exc_info()[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given utterance infos, \
                                     generate csvs with error-specific info.")
    parser.add_argument("projdir", type=str, help="Project directory path")
    args = parser.parse_args()
    Main(args.projdir)
