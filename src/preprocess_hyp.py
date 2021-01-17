"""
Author: coman8
Thesis Study 3
Preprocessing code for the MSFT HUB5 human and ASR transcriptions.

- Expands reduced forms e.g. 'gonna' and 'wanna'
- For abbreviations, strips periods, adds spaces in between abbreviated letters where possible
- Seperates hyphenated words (except backchannels)
- Optionally groups disfluencies into a single class

"""

import os
import argparse


class Main:
	UPDATES = {"'bout":"about",
			   "'cause":"because",
			   "hmm":"hm"}
	REDUCED = {"gonna":("going", "to"), 
			   "wanna":("want", "to"),
			   "kinda":("kind", "of"),
			   "sorta":("sort", "of"),
			   "gotta":("got", "to"),
			   # abbrevs. to expand
			   "hp":("h", "p"),
			   "dj":("d", "j"),
			   "dc":("d", "c"),
			   "ll":("l", "l"),
			   "cre":("c", "r", "e"),
			   "rpm":("r", "p", "m"),
			   "phd":("p", "h", "d"),
			   "twa":("t", "w", "a")}
	HESITATIONS = ["uh", "um", "eh", "hm", 
				   "hmm", "mm", "ah", "huh", 
				   "ha", "er", "oof", "hee", 
				   "ach", "ee", "ew"]
	BACKCHANNELS = ["uh-huh", "um-hum", "mhm"]
			  

	def __init__(self, args):
		files = os.listdir(args.indir)

		for file in files:
			if file.endswith(".ctm"):
				processed = list()
				with open(os.path.join(args.indir, file), 'r') as infile:
					lines = infile.readlines()
				i = 0
				while i < len(lines):
					current = lines[i].split()
					if len(current) > 4:
						current[4] = current[4].lower()
						token = current[4]

						# hyphenation
						if  "-" in token and token != "uh-huh":
							tokens = token.split("-")
							temp = self.get_extension(current,
													  tokens,
													  self.get_endpoint(lines[i+1]))
							processed.extend(temp)

						# abbreviations
						elif token in self.REDUCED:
							temp = self.get_extension(current, 
													  self.REDUCED[token], 
													  self.get_endpoint(lines[i+1]))
							processed.extend(temp)

						# others (include normalize period from ASR abbreviations)
						else:
							if token in self.UPDATES:
								current[4] = self.UPDATES[token]
							if token in self.BACKCHANNELS:
								current[4] = "%backchannel"
							if self.match_split_backchannel(token, lines, i):
								current[4] = "%backchannel"
								i += 1  # the backchannel is uh \n huh, we remove the second line
							if args.disf and token in self.HESITATIONS:
								current[4] = "%hesitation"
							if token.endswith("."):
								current[4] = token.rstrip(".")
							processed.append(current)
					i += 1

				# write processed transcription to file
				outfilename = file[:-4] + "_processed.ctm"
				with open(os.path.join(args.outdir, outfilename), 'w+') as outfile:
					for p in processed:
						outfile.write(' '.join(p))
						outfile.write("\n")

	def match_split_backchannel(self, token, line, i):
		if token != "uh":
			return False
		if i+1 > len(line)-1:
			return False
		if line[i+1][4] == "huh":
			return True
		return False

	def get_endpoint(self, line):
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


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Preprocess transcripts.")
	parser.add_argument("indir", type=str, help="Directory with the transcripts in CTM format.")
	parser.add_argument("outdir", type=str, help="Directory to save new files.")
	parser.add_argument("--disf", action="store_true",
		help="Group disfluencies (e.g. uh, um) into a single hesitations group.")
	args = parser.parse_args()
	Main(args)
