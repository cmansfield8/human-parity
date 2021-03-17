#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" get_error_table.py
Author: coman8@uw.edu

Given the csv of model infos, generates a csv of error info only.
"""

import argparse
import os
from ast import literal_eval
import pandas as pd
import util


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
        c = ['ix', 'annotation', 'position', 'sen_len']
        c.extend(SError.get_columns('hyp'))
        c.extend(SError.get_columns('ref'))
        return c

    def get_data(self):
        d = [self.ix, self.annotation, self.position, self.sen_len]
        d.extend(self.hyp.get_data())
        d.extend(self.ref.get_data())
        return [str(x) for x in d]


class Main:
    ERRORS = ['I', 'D', 'S']

    def __init__(self, projdir):
        for file in os.listdir(projdir):
            if file.endswith('.all'):
                df = util.load_file(projdir, file)

                errors = self.get_errors(df)

                # write file
                output = file[:-4] + '_errors.csv'
                util.write_file(errors, projdir, output,
                                cols=TError.get_columns())

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
        i = util.Counter()
        ann = row['annotation']

        for j in range(len(ann)):
            try:
                atype = ann[j]
            except IndexError:
                util.catch_index_error(ann, j)
                raise

            # since TAG has tokenized contractions, skip those
            i.itercont(row, atype)

            if atype in self.ERRORS:
                e = TError(util.ix_name(ix, j))

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
            util.catch_index_error(row, vars(i))
        return se


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given utterance infos, \
                                     generate csvs with error-specific info.")
    parser.add_argument("projdir", type=str, help="Project directory path")
    args = parser.parse_args()
    Main(args.projdir)
