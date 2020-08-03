#!/apps/bio/software/anaconda2/envs/mathias_general/bin/python3.6
import os
import csv
import sys
import argparse


def prepare_insilico_dict(bedfile, annotationlevel):
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

            annotationlevels = ["1", "2", "3", "4", "5"]
            #  (write 1 if only gene format, 2 = gene_exon_1, 3 = gene_transcript_exon_1, 4 = transcript, 5 = transcript_exon_1)
            if annotationlevel not in annotationlevels:
                print(f"{annotationlevel} not accepted, exiting")
                sys.exit()

            if annotationlevel == "1":
                # Gene
                annotation_dict["gene"] = annotation_name[0]
            elif annotationlevel == "2":
                # Gene_NM_Transcript_Exon_1
                annotation_dict["gene"] = annotation_name[0]
                annotation_dict["transcript"] = '_'.join(annotation_name[1:3])
                annotation_dict["exon"] = '_'.join(annotation_name[3:5])
            elif annotationlevel == "3":
                # Gene_Exon_1
                annotation_dict["gene"] = annotation_name[0]
                annotation_dict["exon"] = '_'.join(annotation_name[1:3])
            elif annotationlevel == "4":
                # NM_Transcript
                annotation_dict["transcript"] = '_'.join(annotation_name[0:2])
            elif annotationlevel == "5":
                # NM_transcript_exon_1
                annotation_dict["transcript"] = '_'.join(annotation_name[0:2])
                annotation_dict["exon"] = '_'.join(annotation_name[2:4])
            else:
                print(f"unexpected annotation format")
                sys.exit()
            print(annotation_dict)
            insilico_list.append(annotation_dict)
    return insilico_list

def annotate_coverage(coverage, bedfile, output, annotationlevel):
    insilico_list = prepare_insilico_dict(bedfile, annotationlevel)
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
    parser.add_argument('-l', '--annotationlevel', nargs='?', help='confusing parameter: (write 1 if only gene format, 2 = gene_transcript_exon_1, 3 = gene_exon_1, 4 = transcript, 5 = transcript_exon_1)', required=True)
    args = parser.parse_args()
    coverage = args.coverage
    bedfile = args.bedfile
    output = args.output
    annotationlevel = args.annotationlevel
    annotate_coverage(coverage, bedfile, output, annotationlevel)

