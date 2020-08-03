#!/apps/bio/software/anaconda2/envs/mathias_general/bin/python3.6
import os
import csv
import sys
import argparse


def merge_low_regions(low_regions):
    sorted_low_regions = sorted(low_regions, key = lambda k:k['start'])
    exon_regions = []
    first_region = sorted_low_regions.pop(0)
    prevstart = first_region["start"]
    prevstop = first_region["stop"]
    merges = 0
    region_dict = {}
    if len(sorted_low_regions) == 0:
        region_dict["start"] = prevstart
        region_dict["stop"] = prevstop
        region_dict["merges"] = 0
        exon_regions.append(region_dict.copy())
        return exon_regions

    iterator = 0
    # Second element starts -->
    for low_region in sorted_low_regions:
        iterator += 1
        start = low_region["start"]
        stop = low_region["stop"]
        if start <= prevstop:
            # region will be merged
            merges += 1
            if stop > prevstop:
                # merge with new stop
                prevstop = stop
            # if last element & to be merged
            if len(sorted_low_regions) == iterator:
                region_dict["start"] = prevstart
                region_dict["stop"] = prevstop
                region_dict["merges"] = merges
                exon_regions.append(region_dict.copy()) 
        else:
            region_dict["start"] = prevstart
            region_dict["stop"] = prevstop
            region_dict["merges"] = merges
            exon_regions.append(region_dict.copy())
            # restart for new region
            merges = 0
            prevstart = start
            prevstop = stop
    return exon_regions    

def low_covered_regions(csvlist, output):
    # chrom, start, stop, gene, transcript, exon
    
    # add all regions together
    # {'chr': '3', 'start': '111319665', 'stop': '111319666', 'gene': 'CD96', 'transcript': 'NM_198196', 'exon': 'exon_8'}

    csvlist = csvlist.split(",")
    exon_dict = {}
    for csv_file in csvlist:
        with open(csv_file, "r") as csv_input:
            fieldnames = ["chr", "start", "stop", "gene", "transcript", "exon"]
            reader = csv.DictReader(csv_input, delimiter=",", fieldnames=fieldnames)
            for low_region in reader:
                # one dict per low covered chr_gene_transcript_exon
                gene_transcript_exon_dict = {k: low_region[k] for k in ('chr', 'gene', 'transcript', 'exon')}
                gene_transcript_exon = '_'.join(str(x) for x in gene_transcript_exon_dict.values())
                #low_region["chr"]["gene"]["transcript"]["exon"]
                low_dict = {}
                low_dict["start"] = int(low_region["start"])
                low_dict["stop"] = int(low_region["stop"])
                #for exon in exon_list:
                    # if exon already exists, append lowdict
                if gene_transcript_exon in exon_dict.keys():
                    exon_dict[gene_transcript_exon].append(low_dict)
                else:
                    exon_dict[gene_transcript_exon] = []
                    exon_dict[gene_transcript_exon].append(low_dict)


    # Now loop through chr_gene_transcript_exons
    # exon_list = {"chr_gene_transcript_exon" : [{"start:" value, "stop": value}, {"start:" value, "stop": value}, ...] etc...}
    with open(output, "w+") as outfile:
        fieldnames = ["gene", "transcript", "exon", "chr", "start", "stop", "merges"]
        writer = csv.DictWriter(outfile, delimiter=",", fieldnames=fieldnames)
        for chr_gene_transc_exon, low_regions in exon_dict.items():
            exon_dict[chr_gene_transc_exon] = merge_low_regions(low_regions)
            for region in exon_dict[chr_gene_transc_exon]:
                name_list = chr_gene_transc_exon.split("_")
                chrom = name_list.pop(0)
                gene = name_list[0]
                transcript = '_'.join(name_list[1:3])
                if "exon" in transcript:
                    transcript = ''
                    exon = '_'.join(name_list[1:3])
                else:
                    exon = '_'.join(name_list[3:5])

                writer.writerow({"gene": str(gene),
                                "transcript": str(transcript),
                                "exon": str(exon),
                                "chr": str(chrom),
                                "merges": str(region["merges"]),
                                "start": str(region["start"]),
                                "stop": str(region["stop"])})
       
        return outfile 
        #print(exon_dict[chr_gene_transc_exon])
    

        # count number of merges to get a number of samples that are low in region

        # Aggregate chr start stop for every gene_transcript_exon in list of dicts
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list_of_csvs', nargs='?', help='(sample1_below10x,sample2_below10x,sample3_below10x)', required=True)
    parser.add_argument('-o', '--output', nargs="?", help='Output file', required=True)
    args = parser.parse_args()
    csvlist = args.list_of_csvs
    output = args.output
    low_covered_regions(csvlist, output)
