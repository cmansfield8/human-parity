"""
Author: coman8
Thesis Chapter 6
Preprocessing code for the reference and hypothesis transcripts prior to SCLITE scoring.
"""

import os
import argparse
import string
import re


def get_prefix(datatype):
	if datatype=="SWBD":
		return "sw_"
	elif datatype=="CH":
		return "en_"
	else:
		return None


class Trans:
	waveform = None
	channel = None
	speaker = None
	begin = None
	end = None
	transcript = None

	def __init__(self, waveid, line, datatype):
		self.waveform = get_prefix(datatype) + waveid
		l = line.split()
		try:
			self.begin = float(l[0])
			self.end = float(l[1])
			self.channel = l[2][:-1]
			self.transcript = ' '.join(l[3:])
		except IndexError as e:
			raise("Corrupt line at file {}: {}".format(self.waveform, line))
		self.speaker = self.waveform + "_" + self.channel
		self.transcript = self.process_str(self.transcript, datatype)

	def process_str(self, sent, datatype):
		if datatype == "SWBD":
			sent = self.normalize_swbd(sent)
		else:
			sent = self.normalize_en(sent) 

		INCOMPLETE = re.compile(r"(-\S*|\S*-)")
		sent = self.sub_word(INCOMPLETE, "", sent)  # incomplete words

		NOISE = re.compile(r"{[^}]+}")    # noise label
		COMMENT = re.compile(r"\[[^\]]+\]+")  # comment
		TAG = re.compile(r"<[^>]+>")  # aside, contraction markers
		INTERRUPT = re.compile(r"--") # interruption markers 

		patterns = [NOISE, COMMENT, TAG, INTERRUPT]
		for p in patterns:
			sent = p.sub("", sent)

		# handle punctuation removal
		punct_keep = {"-", "\'"}
		punct_remove = set(string.punctuation)
		punct_remove.difference_update(punct_keep)
		sent = "".join(ch for ch in sent if ch not in punct_remove)

		sent = sent.strip()  # remove leading and trailing whitespace
		sent = re.sub(r"\s+", " ", sent) # remove double spaces

		# handle empty sentences
		if sent=="":
			sent = "IGNORE_TIME_SEGMENT_IN_SCORING"
		return sent.upper()

	def sub_word(self, pattern, replace, s):
		"""Subs a pattern at a word boundary."""
		BOW = re.compile(r"((?<=\s)|(?<=^))")
		EOW = re.compile(r"((?=\s)|(?<=$))")
		temp = "".join(x.pattern for x in [BOW, pattern, EOW])
		return re.sub(temp, replace, s)

	def normalize_swbd(self, sent):
		WANNA = re.compile(r"wanna", flags=re.I)
		WANNA2 = "want to"
		sent = self.sub_word(WANNA, WANNA2, sent)
		IREP = re.compile(r"i-", flags=re.I)  # should be word
		IREP2 = "i"
		sent = self.sub_word(IREP, IREP2, sent)
		return sent

	def normalize_en(self, sent):
		FOREIGN = re.compile(r"<[\S+]+\s([^>|=]+)>")
		FOREIGN.sub(r"\1", sent)
		return sent

	def toString(self):
		result = [self.waveform, self.channel, self.speaker, self.begin, self.end, self.transcript]
		return "\t".join(str(x) for x in result)


class Main:

	def __init__(self, args):
		processed = list()
		DIGIT=re.compile(r"\d")

		files = os.listdir(args.indir)
		for file in files:
			if file.startswith(get_prefix(args.datatype)):
				with open(os.path.join(args.indir, file), 'r') as infile:
					lines = infile.readlines()
					for line in lines:
						if DIGIT.match(line[0]):  # check line for transcription
							temp = Trans(file[3:7], line, args.datatype)
							processed.append(temp)

		# write processed transcription to file
		outfilename = args.datatype + ".stm"
		with open(os.path.join(args.outdir, outfilename), 'w+') as outfile:
			for t in processed:
				outfile.write(t.toString())
				outfile.write("\n")


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Preprocess transcripts.")
	parser.add_argument("indir", type=str, help="Directory with the transcripts.")
	parser.add_argument("outdir", type=str, help="Directory to save processed transcripts.")
	parser.add_argument("datatype", type=str, help="Transcript type. Expecting one of: SWBD, CH")
	args = parser.parse_args()
	Main(args)