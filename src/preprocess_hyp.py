"""
Author: coman8
Thesis Chapter 6
Preprocessing code for the MSFT transcriptions.

Steps:
	- map reduced forms in UPDATES and REDUCED
		- when extra tokens are created, the timestamp is the midpoint between original token_i and token_i+1
	- lowercase tokens
	- strip periods in abbreviations
	- OPTIONALLY seperate hyphenated words that don't start with uh- or um-
"""

import os
import argparse


class Main:
	UPDATES = {"'bout":"about",
			   "'cause":"because",
			   "hmm":"hm",
			   "mhm":"uh-huh",
			   "till":"until"}
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
						current[4] = current[4].lower()
						token = current[4]

						# handle hyphenation
						if args.dash and "-" in token:
							tokens = token.split("-")
							if tokens[0] not in {"uh", "um"}:
								temp = self.get_extension(current,
															tokens,
															self.endpoint(lines[i+1]))
								processed.extend(temp)
							else:
								processed.append(current)

						# reduced forms 1
						elif token in self.REDUCED:
							temp = self.get_extension(current, 
														  	  self.REDUCED[token], 
													 		  self.endpoint(lines[i+1]))
							processed.extend(temp)

						# more reduced forms and abbreviation normalization
						else:
							if token in self.UPDATES:
								current[4] = self.UPDATES[token]
							if token.endswith("."):
								current[4] = token.rstrip(".")
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
		timepoint = float(arr[2])
		step = float(end - timepoint) / float(len(tokens))

		# edge case where current line ends conversation
		if step < 0:
			timepoint -= 0.004
			step = 0.001
		
		result = list()
		for t in tokens:
			temp = arr.copy()
			temp[2] = "{:.3f}".format(timepoint)
			temp[4] = t
			timepoint += step
			result.append(temp)
		return result 

	def write_debug(self, file, num, line, status):
		print("File {}, Line {}: {} {}".format(file, num, status, line))


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Preprocess transcripts.")
	parser.add_argument("indir", type=str, help="Directory with the transcripts in CTM format.")
	parser.add_argument("outdir", type=str, help="Directory to save new files.")
	parser.add_argument("--dash", action="store_true", help="Seperate certain hypenated words.")
	args = parser.parse_args()
	Main(args)
