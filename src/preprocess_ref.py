"""
Author: coman8@uw.edu
Thesis Study 3

Preprocessing code for the NIST HUB5 reference transcripts prior to SCLITE.

The preprocessing closely follows the initial NIST HUB5 guidelines:
https://mig.nist.gov/MIG_Website/tests/ctr/2000/h5_2000_v1.3.html

- Removes 'comments' about noise, laughter
- Removes formatting symbols and punctuation
- Substitutes and optionally groups hesitations
- Expands reduced forms e.g. 'gonna' and 'wanna'
- Seperates hyphenated words (except for backchannels)
- Fragments have null alternative
- Options to keep all contraction forms or only single-token forms

"""

import os
import argparse
import string
import re


def get_prefix(datatype):
	if datatype == "SWBD":
		return "sw_"
	elif datatype == "CH":
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

	NORMALIZE = [('daycare', 'day care'), ('all right', 'alright'),
				 ('every day', 'everyday'), ('anymore', 'any more'), ('into', 'in to'),
				 ('boyscouts', 'boy scouts'), ('airflow', 'air flow'),
				 ('Bentsy', 'Bensi'), ('Lori', 'Laurie'), ('Leigh', 'Lee'),
				 ('Rachael', 'Rachel'), ('allen', 'alan'),
				 ('Tricia', 'Trisha'), ('Johnny', 'Jonnie'), ('Abby', 'Abbie')]
	HESITATIONS = ["uh", "um", "eh", "hm", "hmm", "mm", "ah", "huh",
				   "ha", "er", "oof", "hee", "ach", "ee", "ew"]
	FRAGMENT_HESITATIONS = ["uh-", "u-", "a-", "e-"]
	BACKCHANNELS = ["uh-huh", "um-hum", "mhm"]
	EMPTY = "IGNORE_TIME_SEGMENT_IN_SCORING"

	def __init__(self, waveid, line, datatype):
		self.waveform = get_prefix(datatype) + waveid
		l = line.split()
		try:
			self.begin = float(l[0])
			self.end = float(l[1])
			self.channel = l[2][:-1]
			if self.channel == "B1":
				self.channel = "B"
			self.transcript = ' '.join(l[3:])
		except IndexError:
			raise("Corrupt line at file {}: {}".format(self.waveform, line))
		self.speaker = self.waveform + "_" + self.channel
		self.transcript = self.process_str(self.transcript, datatype)

	def process_str(self, sent, datatype):

		# special label for noise (will match alternative pronunciations)
		NOISE = re.compile(r"{[^}]+}")
		sent = NOISE.sub("", sent)

		# contraction label
		if args.cont:
			CONT1 = re.compile(r"<contraction e_form=\"\[[^=]+=>([^\]]+)\]\">(\S+)")
			sent = CONT1.sub(r"{ \1 / \2 }", sent)

			CONT2 = re.compile(r"<contraction e_form=\"\[[^=]+=>([^=]+)\]\[[^=]+=>([^=]+)\]\">(\S+)")
			sent = CONT2.sub(r"{ \1 \2 / \3 }", sent)
		else:
			CONT = re.compile(r"<contraction e_form=\"(\[[^=]+=>[^=]+\])+\">")
			sent = CONT.sub(r"", sent)

		# type-specific processing
		if datatype == "SWBD":
			sent = self.normalize_swbd(sent)
		else:
			sent = self.normalize_en(sent)

		# various special labels
		COMMENT = re.compile(r"\[[^\]]+\]+")  # comment (warning: will match contractions)
		TAG = re.compile(r"<[^>]+>")  # aside (warning: will match contractions)
		DDASH = re.compile(r"//")  # aside
		INTERRUPT = re.compile(r"--")  # interruption markers

		patterns = [COMMENT, TAG, DDASH, INTERRUPT]
		for p in patterns:
			sent = p.sub("", sent)

		# strip punctuation
		punct_keep = {"-", "\'", "/", "{", "}", "_"}
		punct_remove = set(string.punctuation)
		punct_remove.difference_update(punct_keep)
		sent = "".join(ch for ch in sent if ch not in punct_remove)

		sent = sent.strip()  # leading and trailing whitespace
		sent = re.sub(r"\s+", " ", sent)  # remove double spaces

		# fragments
		INCOMPLETE = re.compile(r"(\S+-|-\S+)")
		sent = self.sub_word(INCOMPLETE, r"{ \2 / @ }", sent)

		# normalize
		for varients in self.NORMALIZE:
			for v in varients:
				if re.search(v, sent):
					alt = self.get_alt(varients)
					sent = self.sub_word(re.compile(v), alt, sent)
					break

		# disfluency related normalizations
		sent = self.sub_word(re.compile(r"hmm"), "hm", sent)
		sent = self.sub_word(re.compile(r"ooh"), "oh", sent)

		if args.disf:
			sent = self.sub_hesitations(sent)

		# matches MSFT transcript conventions, otherwise WER is extremely high
		sent = self.sub_word(re.compile(r"uh-huh"), r"%backchannel", sent)
		sent = self.sub_word(re.compile(r"um-hum"), r"%backchannel", sent)
		# according to NIST guidelines
		sent = self.sub_word(re.compile(r"mhm"), r"%backchannel", sent)

		# hyphenation
		DASHED = re.compile(r"([^uh|um|\s])-(\S)")
		sent = DASHED.sub(r"\1 \2", sent)

		# fix segmentation fault before it happens, you'll thank yourself later
		YALLVE = re.compile(r"y'{ all have / all've }")
		sent = YALLVE.sub("{ you all have / y'all have / y'all've }", sent)

		# empty sentences
		if sent != self.EMPTY:
			sent = sent.lower()
		if sent == "":
			sent = self.EMPTY
		return sent

	def sub_word(self, pattern, replace, s):
		"""Subs a pattern within a word boundary."""
		BOW = re.compile(r"((?<=\s)|(?<=^))")
		EOW = re.compile(r"((?=\s)|(?<=$))")
		temp = "".join(x.pattern for x in [BOW, pattern, EOW])
		return re.sub(temp, replace, s)

	def sub_hesitations(self, s):
		# tag hesitations
		for h in self.HESITATIONS:
			s = self.sub_word(re.compile(h), r"%hesitation", s)
		for fh in self.FRAGMENT_HESITATIONS:
			FRAGH = re.compile(r"({})".format(fh))
			s = self.sub_word(FRAGH, r"\2 / %hesitation", s)
		return s

	def normalize_swbd(self, sent):
		sent = self.sub_word(re.compile(r"gonna"), "going to", sent)
		sent = self.sub_word(re.compile(r"wanna"), "want to", sent)
		GUESS = re.compile(r"([^\s]+)\[([^\]]+)]")
		sent = GUESS.sub(r"\1\2", sent)
		return sent

	def normalize_en(self, sent):
		FOREIGN = re.compile(r"<[\S+]+\s([^>|=]+)>")
		FOREIGN.sub(r"\1", sent)
		return sent

	def get_alt(self, l):
		return "{ " + " / ".join(l) + " }"

	def toString(self):
		result = [self.waveform, self.channel, self.speaker, self.begin,
				  self.end, self.transcript]
		return "\t".join(str(x) for x in result)


class Main:

	def __init__(self, args):
		processed = list()
		DIGIT = re.compile(r"\d")

		files = os.listdir(args.indir)
		for file in files:
			if file.startswith(get_prefix(args.datatype)):
				print("Cleaning file {}".format(file))
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


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Preprocess transcripts.")
	parser.add_argument("indir", type=str, help="Directory with transcripts.")
	parser.add_argument("outdir", type=str, help="Directory to save post-processed transcripts.")
	parser.add_argument("datatype", type=str, help="Transcript type. Expecting one of: SWBD, CH")
	parser.add_argument("--cont", action="store_true",
						help="Include both reduced and expanded contraction forms (default is reduced).")
	parser.add_argument("--disf", action="store_true",
						help="Group disfluencies (e.g. uh, um) into a single hesitations group.")
	args = parser.parse_args()
	Main(args)
