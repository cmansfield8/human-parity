#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" token_freq_stats.py
Author: coman8@uw.edu

Makes text files of the hypothesis and reference sentences for downstream processing
"""

import argparse
import os
import pandas as pd
from ast import literal_eval

class Main:

	def __init__(self, args):
		#load file
		for file in os.listdir(args.projdir):
			if file.endswith('.ctm.csv'):
				print('Loaded: {}'.format(file))
				infile = os.path.join(args.projdir, file)
				df = pd.read_csv(infile, index_col=0)
				
				output = os.path.join(args.projdir, file[:-8])
				
				self.get_sent_txt(df['hyp_sent'], output + '_hyp.txt')
				self.get_sent_txt(df['ref_sent'], output + '_ref.txt')
				
	def get_sent_txt(self, series, outfile):
		result = series.apply(lambda x: literal_eval(x))
		result =  result.tolist()
		for i in range(len(result)):
			result[i] = [x for x in result[i] if x != ""]
		result = [' '.join(x) for x in result]
		
		with open(outfile, 'w+') as out:
			for r in result:
				out.write(r + '\n')

if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Produces both sentence alternatives as .txt files for downstream modeling.")
	parser.add_argument("projdir", type=str, help="Project directory path")
	args = parser.parse_args()
	Main(args)
