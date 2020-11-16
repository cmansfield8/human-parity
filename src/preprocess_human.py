"""
Author: coman8
Thesis Chapter 6
Preprocessing code for the MSFT human transcriptions.

Args:
	- indir : expecting a directory which includes human transcript files in CTM format, with file substring "human".
"""

import os
import argparse
import re


class Main:
	UPDATES = {"'BOUT":"ABOUT",
			   "'CAUSE":"BECAUSE",
			   "HMM":"HM"}
	REDUCED = {"GONNA":("GOING", "TO"), 
			   "WANNA":("WANT", "TO"),
			   "KINDA":("KIND", "OF"),
			   "SORTA":("SORT", "OF")}

	def __init__(self, args):
		files = os.listdir(args.indir)

		for file in files:
			if file.startswith("human") and file.endswith(".ctm"):
				processed = list()
				with open(os.path.join(args.indir, file), 'r') as infile:
					lines = infile.readlines()
				for i in range(len(lines)):
					current = lines[i].split()
					if len(current) > 4 and current[4] in self.UPDATES:
						self.write_debug(file, i, current, "updated")
						processed.append(self.UPDATES[current[4]])
					elif len(current) > 4 and current[4] in self.REDUCED:
						self.write_debug(file, i, current, "reduced")
						timestamp = float(lines[i+1].split()[2])
						temp1, temp2 = self.get_extension(current, timestamp)
						processed.extend([temp1, temp2])
					else:
						processed.append(current)

				# write processed transcription to file
				outfilename = file[:-4] + "_processed.ctm"
				with open(os.path.join(args.outdir, outfilename), 'w+') as outfile:
					for p in processed:
						outfile.write(' '.join(p))
						outfile.write("\n")

	def get_extension(self, line, stop):
		token1, token2 = self.REDUCED[line[4]]
		line[4] = token1
		next_line = line.copy()
		next_line[4] = token2
		start = float(next_line[2])
		mid = start + float(stop - start) / 2
		next_line[2] = str(mid)
		return line, next_line

	def write_debug(self, file, num, line, status):
		print("File {}, Line {}: {} line {}".format(file, num, status, line))


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Preprocess transcripts.")
	parser.add_argument("indir", type=str, help="Directory with the transcripts.")
	parser.add_argument("outdir", type=str, help="Directory to save new files.")
	parser.add_argument("debug", type=bool, help="Debug mode.")
	args = parser.parse_args()
	Main(args)
