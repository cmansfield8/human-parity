#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" get_error_table.py
Author: coman8@uw.edu

Given the utterance table, generates a csv of errors.
"""

import argparse
import os
import re
from ast import literal_eval
import pandas as pd


class Main:
	ERRORS = ['I', 'D', 'S']

	def __init__(self, args):
		for file in os.listdir(args.projdir):
			if file.endswith('ctm.csv'):
				#load file
				infile = os.path.join(args.projdir, file)
				indf = pd.read_csv(infile, index_col=0)
				
				# read columns as list
				columns = ['annotation', 'hyp_sent', 'ref_sent']
				for c in columns:
					indf[c] = indf[c].apply(lambda x: literal_eval(x))
				
				# get errors
				result = self.extract_errors(indf)
				column_names = ['id', 'annotation', 'hyp_token', 'ref_token']
				outdf = pd.DataFrame.from_dict(result, orient='index', columns=column_names)

				# write file
				output = file[:-3] + 'errors.csv'
				outdf.to_csv(os.path.join(args.projdir, output))

	def extract_errors(self, df):
		result = dict()
		for ix, row in df.iterrows():
			ann = row['annotation']
			counter = 0
			for i in range(len(ann)):
				if ann[i] in self.ERRORS:
					temp = list()
					temp.append(ix)
					temp.append(ann[i])
					temp.append(row['hyp_sent'][i])
					temp.append(row['ref_sent'][i])

					key = re.sub(r"\((.+)\)", r"\1", ix)
					key = key + "#" + str(counter)
					result[key] = temp
					counter += 1
		return result


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Given an utterance table, generates a csv with error infos.")
	parser.add_argument("projdir", type=str, help="Project directory path")
	args = parser.parse_args()
	Main(args)
