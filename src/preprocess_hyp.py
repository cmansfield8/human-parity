"""
Author: coman8
Thesis Chapter 6
Preprocessing code for the MSFT transcriptions.

Steps:
	- maps reduced forms in UPDATES and REDUCED
		- when extra tokens are created, the timestamp is the midpoint between original token_i and token_i+1
	- lowercase tokens
	- strips periods in abbreviations
"""

import os
import argparse


class Main:
	UPDATES = {"'bout":"about",
			   "'cause":"because",
			   "hmm":"hm",
			   "mhm":"uh-huh"}
	REDUCED = {"gonna":("going", "to"), 
			   "wanna":("want", "to"),
			   "kinda":("kind", "of"),
			   "sorta":("sort", "of")}

	def __init__(self, args):
		files = os.listdir(args.indir)

		for file in files:
			if file.endswith(".ctm"):
				processed = list()
				with open(os.path.join(args.indir, file), 'r') as infile:
					lines = infile.readlines()
				for i in range(len(lines)):
					current = lines[i].split()
					if len(current) > 4:
						token = current[4].lower()
						if token in self.REDUCED:
							temp1, temp2 = self.get_extension(current, 
														  	  self.REDUCED[token], 
													 		  self.endpoint(lines[i+1]))
							processed.extend([temp1, temp2])
						else:
							if token in self.UPDATES:
								token = self.UPDATES[token]
							if token.endswith("."):
								token = token.rstrip(".")
							current[4] = token
							processed.append(current)

				# write processed transcription to file
				outfilename = file[:-4] + "_processed.ctm"
				with open(os.path.join(args.outdir, outfilename), 'w+') as outfile:
					for p in processed:
						outfile.write(' '.join(p))
						outfile.write("\n")


	def endpoint(self, line):
		return float(line.split()[2])

	def get_extension(self, arr, tokens, end):
		arr[4] = tokens[0]
		start = float(arr[2])
		mid = start + float(end - start) / 2
		temp = arr.copy()
		temp[2] = "{:.3f}".format(mid)
		temp[4] = tokens[1]
		return arr, temp


	def write_debug(self, file, num, line, status):
		print("File {}, Line {}: {} {}".format(file, num, status, line))


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Preprocess transcripts.")
	parser.add_argument("indir", type=str, help="Directory with the transcripts in CTM format.")
	parser.add_argument("outdir", type=str, help="Directory to save new files.")
	args = parser.parse_args()
	Main(args)
