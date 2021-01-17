#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" token_freq_stats.py
Author: coman8@uw.edu

Produces the top errors for each error category in each error set
"""

import argparse
import os
import numpy as np
import pandas as pd


class Main:
	LABELS = ['I', 'D', 'S']

	def __init__(self, args):
		for file in os.listdir(args.projdir):
			if file.endswith('ctm.errors.csv'):

				#load file
				print('Loaded: {}'.format(file))
				infile = os.path.join(args.projdir, file)
				df = pd.read_csv(infile, index_col=0)
				df = df.replace(np.nan, "", regex=True)
				df['comb_token'] = df['hyp_token'] + '_' + df['ref_token']


				for label in self.LABELS:
					print('Label: {}'.format(label))
					temp= df[df['annotation'] == label]
					grouped = temp[['comb_token', 'id']].groupby('comb_token').count()
					grouped.rename(columns={'id':'count'}, inplace=True)
					grouped.sort_values('count', ascending=False, inplace=True)
					print(grouped.head(args.top))
					print('\n')



if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Given an error table, retrieves top errors.")
	parser.add_argument("projdir", type=str, help="Project directory path")
	parser.add_argument("--top", type=int, default=30, help="Number of top errors to display")
	args = parser.parse_args()
	Main(args)
