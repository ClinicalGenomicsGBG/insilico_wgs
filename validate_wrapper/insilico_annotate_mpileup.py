#!/apps/bio/software/anaconda2/envs/mathias_general/bin/python3.6
import os
import csv
import sys
import argparse


def prepare_insilico_dict(bedfile):
    with open(bedfile, "r") as bedfile:
        insilico_list = []
        for annotationrow in bedfile:
            annotation_dict = {}
            annotation_info = annotationrow.split("\t")[:-1]
            annotation_dict["chrom"] = annotation_info[0]
            annotation_dict["start"] = annotation_info[1]
            annotation_dict["stop"] = annotation_info[2]
            annotation_name = annotation_info[3].split("_")
            # Possibly annotation formats
            # GENE_NM_XXXXXXXX_Exon_X
            # GENE_Exon_X
            # NM_XXXXXXXX_Exon_X
            # NM_XXXXXXXX
            # GENE
            # Discover format
            annotation_len = len(annotation_name)
            print(annotation_name)
            if annotation_len == 1:
                # Only Genes
                annotation_dict["gene"] = annotation_name[0]
            elif annotation_len == 2:
                # Only Transcript
                transcript = '_'.join(annotation_name[0:1])
                annotation_dict["transcript"] = transcript
            elif annotation_len == 3:
                # Gene + Exon
                annotation_dict["gene"] = annotation_name[0]
                exon = '_'.join(annotation_name[1:2])
                annotation_dict["exon"] = exon
            elif annotation_len == 4:
                # Transcript + Exon
                transcript = '_'.join(annotation_name[0:1])
                exon = '_'.join(annotation_name[1:2])
                annotation_dict["transcript"] = transcript
                annotation_dict["exon"] = exon
            elif annotation_len == 5:
                # Gene + Transcript + Exon
                annotation_dict["gene"] = annotation_name[0]
                transcript = '_'.join(annotation_name[0:1])
                exon = '_'.join(annotation_name[1:2])
                annotation_dict["transcript"] = transcript
                annotation_dict["exon"] = exon
            else:
                print(f"unexpected annotation format: {annotation_name}")
                sys.exit()
            print(annotation_dict)
            insilico_list.append(annotation_dict)
    return insilico_list

def annotate_coverage(coverage, bedfile, output):
    insilico_list = prepare_insilico_dict(bedfile)
    if output.endswith('/'):
        output = output[:-1]
    #if not os.path.isdir(output):
        #print(f"{output} does not point to an existing directory. Changing to dirname of path.")
        #output = os.path.dirname(output)
        #sys.exit()
     

    #with open(f"{output}/{os.path.basename(coverage)}_annotated.csv", 'w') as csvout:
    #Bättre att output-filnamnet är det man skriver som argument
    with open(output, 'w+') as csvout:
        csv_writer = csv.writer(csvout)
        coverage_list = []
        with open(coverage, "r") as coverage:
            for covrow in coverage:
                cov_list = covrow.rstrip('\n').split("\t")
                for region in insilico_list:
                    # LFM1 does not pass below check
                    
                    if int(cov_list[1]) >= int(region["start"]) and int(cov_list[1]) <= int(region["stop"]) and str(cov_list[0]) == str(region["chrom"]):
                            try:
                                cov_list.append(region["gene"])
                            except:
                                pass
                            try:
                                cov_list.append(region["transcript"])
                            except:
                                pass
                            try:
                                cov_list.append(region["exon"])
                            except:
                                pass
                coverage_list.append(cov_list)
        csv_writer.writerows(coverage_list)


def runner(coverage, bedfile):
    insilico_list = prepare_insilico_dict(bedfile)
    coverage_list = []
    for covrow in coverage:
                cov_list = covrow.rstrip('\n').split("\t")
                for region in insilico_list:
                    if cov_list[1] >= region["start"] and cov_list[1] <= region["stop"] and cov_list[0] == region["chrom"]:
                            try:
                                cov_list.append(region["gene"])
                            except:
                                pass
                            try:
                                cov_list.append(region["transcript"])
                            except:
                                pass
                            try:
                                cov_list.append(region["exon"])
                            except:
                                pass
                coverage_list.append(cov_list)
    return coverage_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--coverage', nargs='?', help='(from samtools mpileup -l $BED -Q 1 $BAM | cut -f1,2,4)', required=True)
    parser.add_argument('-b', '--bedfile', nargs='?', help='(annotate coverage-positions with Gene Transcript Exonnumber)', required=True)
    parser.add_argument('-o', '--output', nargs='?', help='(Output location)', required=True)
    args = parser.parse_args()
    coverage = args.coverage
    bedfile = args.bedfile
    output = args.output
    annotate_coverage(coverage, bedfile, output)

