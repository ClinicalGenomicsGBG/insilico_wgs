#!/apps/bio/software/anaconda2/envs/mathias_general/bin/python3.6
import os
import argparse
import sys
import csv

def expand_regions(expand, start, stop):
	start -= expand
	stop += expand
	return int(start), int(stop)

def create_refseq_dict(gtf, keep_cols_dict):
	refseq_dict = {}
	with open(gtf, 'r') as refgtf:
		first_line = refgtf.readline().split("\t")
		for transcript in refgtf:
			transcriptlist = transcript.split("\t")
			refseq_dict[transcriptlist[keep_cols_dict["name"]]] = {}
			refseq_dict[transcriptlist[keep_cols_dict["name"]]]["transcript"] = transcriptlist[keep_cols_dict["name"]]
			refseq_dict[transcriptlist[keep_cols_dict["name"]]]["gene"] = transcriptlist[keep_cols_dict["name2"]]
			refseq_dict[transcriptlist[keep_cols_dict["name"]]]["t_start"] = transcriptlist[keep_cols_dict["txStart"]]
			refseq_dict[transcriptlist[keep_cols_dict["name"]]]["t_stop"] = transcriptlist[keep_cols_dict["txEnd"]]
			refseq_dict[transcriptlist[keep_cols_dict["name"]]]["t_chrom"] = transcriptlist[keep_cols_dict["chrom"]]
			refseq_dict[transcriptlist[keep_cols_dict["name"]]]["t_exonstart"] = transcriptlist[keep_cols_dict["exonStarts"]].split(",")[:-1]
			refseq_dict[transcriptlist[keep_cols_dict["name"]]]["t_exonstop"] = transcriptlist[keep_cols_dict["exonEnds"]].split(",")[:-1]
			refseq_dict[transcriptlist[keep_cols_dict["name"]]]["t_strand"] = transcriptlist[keep_cols_dict["strand"]]
	return refseq_dict

def create_write_dict(chrom, start, stop, name, strand):
	write_dict = {}
	write_dict["chrom"] = chrom
	write_dict["start"] = start
	write_dict["stop"] = stop
	write_dict["name"] = name
	write_dict["strand"] = strand
	return write_dict


def longest_transcript(transcript_dict_list):
	length_dict = {}
	for transcript_dict in transcript_dict_list:
		transcript = transcript_dict["transcript"]
		t_start = int(transcript_dict["t_start"])
		t_stop = int(transcript_dict["t_stop"])
		t_length = t_stop - t_start
		length_dict[transcript] = t_length
	longest_transcript = max(length_dict, key=length_dict.get)
	return longest_transcript

def whole_gene_region(transcript_dict_list):
	transcript_starts = []
	transcript_ends = []
	example_transcript = transcript_dict_list[0]
	genename = example_transcript["gene"]
	strand = example_transcript["t_strand"]	
	chrom = example_transcript["t_chrom"]

	for transcript in transcript_dict_list:
		transcript_starts.append(transcript["t_start"])
		transcript_ends.append(transcript["t_stop"])
		
	gene_start = min(transcript_starts)
	gene_stop = max(transcript_ends)
	
	write_dict = create_write_dict(chrom, gene_start, gene_stop, genename, strand)
	return write_dict		


def append_transcript_exonregions(genename, transcript_dict, write_table, expand):
	transcript = transcript_dict["transcript"]
	chrom = transcript_dict["t_chrom"]
	strand = transcript_dict["t_strand"]
	exonstarts = transcript_dict["t_exonstart"]
	exonends = transcript_dict["t_exonstop"]
	num_exons = len(exonstarts)
	for exoniter, exonstart in enumerate(exonstarts):
		if strand == "-":
			exonname = f"exon_{num_exons - exoniter}"
		else:
			exonname = f"exon_{exoniter + 1}"

		exonstart = int(exonstart)
		exonstop = int(exonends[exoniter])

		# Expand regions if asked for
		if expand:
			exonstart, exonstop = expand_regions(expand, exonstart, exonstop)

		# Define write dict
		exon_write_dict = create_write_dict(chrom, exonstart, exonstop, f"{genename}_{transcript}_{exonname}", strand)
		write_table.append(exon_write_dict)
	return write_table

def write_not_found(not_found_table, target_filename, output):
	if not_found_table:
		with open(f"{output}/{target_filename}_notfound.txt", "w") as notfound:
			notfound.write(f"Some genes in {target_filename} were not found:\n")
			for not_found in not_found_table:
				notfound.write(f"{not_found}\n")
	else:
		return
	
def write_bedfile(write_table, target_filename, output):
	with open(f"{output}/{target_filename}.bed", 'w', newline='') as bedfile:
		fieldnames = ["chrom", "start", "stop", "name", "strand"]
		writebed = csv.DictWriter(bedfile, fieldnames=fieldnames, delimiter='\t')
		for bedline in write_table:
			writebed.writerow(bedline)

def refseq_gene(gtf, expand, targetgenes, output, transcripts, longest):
	if output.endswith('/'):
		output = output[:-1]

	with open(gtf, 'r') as refgtf:
		header = refgtf.readline().split("\t")
		keep_cols = ["name", "chrom", "strand", "txStart", "txEnd", "name2", "exonStarts", "exonEnds"]
		keep_cols_dict = {}
		for keepcol in keep_cols:
			for colnumber, column in enumerate(header):
				if column == keepcol:
					keep_cols_dict.update({keepcol:colnumber})
		
	refseq_dict = create_refseq_dict(gtf, keep_cols_dict)

	# OUTPUT LISTS
	not_found_table = []
	write_table = []

	# TRANSCRIPTS SUPPLIED
	if transcripts:
		target_filename = os.path.basename(transcripts)
		# Read transcriptlist file
		with open(transcripts, "r") as transcriptfile:
			transcriptlist = []
			for transcriptname in transcriptfile:
				transcriptname = transcriptname.rstrip('\n')
				transcriptlist.append(transcriptname)

		# Loop through transript list and define write_table to create bedfile
		for transcript in transcriptlist:
			try:
				genename = refseq_dict[transcript]["gene"]
			except:
				# transcript.version not found
				# try transcript.AnyVersion
				transcript_any = transcript.split(".")[0]
				for ref_transcript in refseq_dict:
					if f"{transcript_any}." in ref_transcript:
						not_found_table.append(f"Missing version {transcript}, found: {ref_transcript}")
						transcript = ref_transcript
				try:
					genename = refseq_dict[transcript]["gene"]	
				except:
					not_found_table.append(f"Missing transcript: {transcript}")
					continue		
			write_table = append_transcript_exonregions(genename, refseq_dict[transcript], write_table, expand)

	# GENES SUPPLIED
	elif targetgenes:
		target_filename = os.path.basename(targetgenes)
		with open(targetgenes, 'r') as targetgenes:
			target_genelist = []
			for gene in targetgenes:
				gene = gene.rstrip('\n')
				target_genelist.append(gene)
		
		for genename in target_genelist:
			transcript_dict_list = []
			for transcript in refseq_dict:
				if refseq_dict[transcript]["gene"] == genename:
					transcript_dict_list.append(refseq_dict[transcript])
			if not transcript_dict_list:
				not_found_table.append(f"Missing gene: {genename}")
				continue

			# LONGEST TRANSCRIPT OUTPUT
			if longest:
				transcript = longest_transcript(transcript_dict_list)
				write_table = append_transcript_exonregions(genename, refseq_dict[transcript], write_table, expand)
			# GENE OUTPUT
			else:
				write_gene = whole_gene_region(transcript_dict_list)
				write_table.append(write_gene)

	else:
		print("Must supply either genelist or transcriptlist")
		sys.exit()

	write_not_found(not_found_table, target_filename, output)
	if expand:
		target_filename = f"{target_filename}_ext{expand}"

	# Sort and write table
	write_table = sorted(write_table, key=lambda k: k['chrom'])
	write_bedfile(write_table, target_filename, output)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-r', '--refseqgtf', nargs='?', help='Input Refseq GTF file with transcripts, will output bedfile based on longest gene-region', required=True)
	parser.add_argument('-g', '--genenames', nargs='?', help='Input Genelist in Refseq format to extract to bedfile (one gene per row)', required=False)
	parser.add_argument('-t', '--transcripts', nargs='?', help='Input Transcriptlist in Refseq format to extract to bedfile (one exon per row)', required=False)
	parser.add_argument('-l', '--longest', nargs='?', help='OBS: Only applicable in case of gene list. Extracts longest transcript.', required=False)
	parser.add_argument('-e', '--expand', nargs='?', help='expand regions (+/-) with bases supplied', default=0,  type=int, required=False)
	parser.add_argument('-o', '--output', nargs='?', help='location to output results', required=True)
	args = parser.parse_args()
	refseq_gene(args.refseqgtf, args.expand, args.genenames, args.output, args.transcripts, args.longest)
