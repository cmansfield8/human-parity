"""
A script to get a vocabulary file for a stm or ctm formatted text.
"""

import argparse
import os
import re
from collections import defaultdict
import pandas as pd


class Main:

	def __init__(self, args):
		result = list()

		if args.ftype=="CH":
			labels = ['callhome', 'CH']
		else:
			labels = ['swb', 'SWBD']

		# make vocabulary for each file
		for file in os.listdir(args.indir):
			if file.endswith(".ctm") and labels[0] in file:
				temp = self.get_voc(os.path.join(args.indir, file), "ctm")
				result.append((file, temp))
			if file.endswith("O.stm") and labels[1] in file:
				temp = self.get_voc(os.path.join(args.indir, file), "stm")
				result.append((file, temp))

		# get total vocabulary
		all_tokens = set()
		for _, v in result:
			all_tokens.update(v.keys())

		# add vocabulary to frequency table
		df = pd.DataFrame(index=sorted(list(all_tokens)))
		for column, v in result:
			temp = pd.Series(v)
			df[column] = temp

		# print frequency table
		df = self.sort_freq(df, labels[1] + 'O.stm')
		df.to_csv(os.path.join(args.indir, labels[1] + '.vocab'), sep='\t')


	def get_voc(self, infile, dtype):
		vocab = defaultdict(int)

		if dtype == "stm":
			df = pd.read_csv(infile, sep='\t')
			sents = df.iloc[:,-1].tolist()
			for s in sents:
				s = re.sub(r"{(\s[-|\w|\']+\s)\/[^}]+}", r"\1", s)
				if "{" in s:
					print(s)
				s = s.split()
				for t in s:
					vocab[t] += 1
		else:
			df = pd.read_csv(infile, sep=' ')
			toks = df.iloc[:, 4].tolist()
			for t in toks:
				vocab[t] += 1

		return vocab


	def sort_freq(self, df, colname):
		return df.sort_values(colname, ascending=False)


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Get vocab and counts for transcripts.")
	parser.add_argument("indir", type=str, help="Data dir with transcripts")
	parser.add_argument("ftype", type=str, help="One of SWBD or CH.")
	args = parser.parse_args()
	Main(args)

