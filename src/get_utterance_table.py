#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" get_utterance_table.py
Author: coman8@uw.edu

Given the sgml files, parses them and saves them in a table, with 1 utterance per row.

Also generates:
	- Hypothesis sentence
	- Reference sentence
	- Error annotation
"""

import argparse
import os
import re
import pandas as pd
from bs4 import BeautifulSoup

class Main:
	LABELS = ['C', 'S', 'I', 'D']

	def __init__(self, args):
		column_names = ['speakerid', 'word_cnt', 'filename', 'channel', 'sequence', 'r_t1', 
								'r_t2', 'word_aux', 'raw_sent']

		for file in os.listdir(args.projdir):
			if file.endswith('sgml'):

				# read file
				with open(os.path.join(args.projdir, file), 'r') as infile:
					text = infile.read()
				soup=BeautifulSoup(text, 'html.parser')
			
				# generate dataframe
				data= self.get_structured_data(soup)
				df = pd.DataFrame.from_dict(data, orient='index', columns=column_names)
				df['annotation'] = df['raw_sent'].apply(lambda x: self.get_annotation(x))
				df['hyp_sent'] = df['raw_sent'].apply(lambda x: self.get_sentence(x, ftype='hyp'))
				df['ref_sent'] = df['raw_sent'].apply(lambda x: self.get_sentence(x, ftype='ref'))

				# write output
				hyp_fname = soup('system')[0].attrs['hyp_fname'].split('/')[-1]
				df.to_csv(os.path.join(args.projdir, hyp_fname + '.csv' ))

	
	def get_structured_data(self, data):
		results = dict()
		for sp in data('speaker'):
			speakerid = sp['id']
			for x in sp('path'):
				temp = list()
				temp.append(speakerid)
				d = x.attrs
				results_key = d.pop('id')
				for k in d.keys():
					temp.append(d[k])
				utterance = self.parse_contents(x.contents)
				temp.append(utterance)
				assert(len(temp))==9
				results[results_key] = temp
		return results


	def parse_contents(self, s):
		result = re.sub(r"\n(.*)\n", r"\1" , s[0])
		result = result.split(',')
		result = [i.strip("\"") for i in result]
		return result

	def get_annotation(self, raw_sent):
		ann = [raw_sent[i] for i in range(0, len(raw_sent), 4)]
		ann = [i.split(':')[-1] for i in ann]
		ann = [i for i in ann if i in self.LABELS]
		return ann

	def get_sentence(self, raw_sent, ftype):
		if ftype == 'ref':
			sent = [raw_sent[i+1] for i in range(0, len(raw_sent)-1, 4)]
		elif ftype == 'hyp':
			sent = [raw_sent[i+2] for i in range(0, len(raw_sent)-2, 4)]
		sent = [i.strip("\"") for i in sent]
		return sent


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Parses sgml files to csv with \
												  1 utterance per row.")
	parser.add_argument("projdir", type=str, help="Project directory path")
	args = parser.parse_args()
	Main(args)

