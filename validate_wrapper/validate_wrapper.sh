#!/bin/bash -l

create_dir()
{
if [ ! -d "$1" ];
then
    mkdir $1
fi
}

BEDFILE=$(echo "$1")
DEPARTMENT=$(echo "$2")
LEVEL=$(echo "$3")

if [ "$DEPARTMENT" == "KG" ];
then
    department=$(echo "klinisk_genetik")
elif [ "$DEPARTMENT" == "KK" ];
then
    department=$(echo "klinisk_kemi")
else
    echo "invalid department, exiting"
    exit
fi
if [ -z "$LEVEL" ]; then
    echo "LEVEL input: $LEVEL is empty. Input, 1,2,3,4 or 5."
    echo "Refers to annotationtype in bedfile...a bit confusing, sorry" 
    echo "1 = GENE"
    echo "2 = GENE_NM_TRANSCRIPT_EXON_X"
    echo "3 = GENE_EXON_X"
    echo "4 = NM_TRANSCRIPT"
    echo "5 = NM_TRANSCRIPT_EXON_X"
fi

# Bamfiles for validation
BAMFILES=/medstore/Development/WGS_validation/coverage_analysis/PCRfree_bamlinks

OUTPUT=$(echo "/medstore/Development/WGS_validation/in_silico_panels/${department}/validate/panels/$(basename $BEDFILE)")

mpileup()
{
create_dir "$OUTPUT"
create_dir "$OUTPUT/mpileup"

for bamfile in $(find $BAMFILES -name "*bam" | grep -v "males" | grep -v "females");
do
    if [ "$(find /medstore/Development/WGS_validation/coverage_analysis/PCRfree_bamlinks -name "*bam" | grep -v "females" | grep -v "males" | tail -n 1)" = "${bamfile}" ];
    then
        qsub -sync y samtools_mpileup.sh $bamfile $BEDFILE $OUTPUT/mpileup
    else
        qsub samtools_mpileup.sh $bamfile $BEDFILE $OUTPUT/mpileup
    fi
done

sleep 50m
}

annotate()
{
create_dir "$OUTPUT/mpileup/annotated"
for mpileup in $(find $OUTPUT -name "*.tsv");
do
    ./insilico_annotate_mpileup.py -c $mpileup -b $BEDFILE -l $LEVEL -o $OUTPUT/mpileup/annotated/$(basename $mpileup | cut -d"." -f1)_annotated.tsv
done
}

getstats()
{
create_dir "$OUTPUT/general_stats"
for mpileup in $(find $OUTPUT -name "*.tsv" | grep -v "annotated");
do
    stats=$(./insilico_stats.py -c $mpileup -t 1,5,10,20)
    header=$(echo "$stats" | sed "1q;d")
    stats=$(echo "$stats" | sed "2q;d")
    if [ ! -f $OUTPUT/general_stats/$(basename $BEDFILE)_stats.tsv ];
    then
        echo "$heeader" > $OUTPUT/general_stats/$(basename $BEDFILE)_stats.tsv
    fi 
    echo -e "$(basename $mpileup | cut -d"." -f1)\t$stats" >> $OUTPUT/general_stats/$(basename $BEDFILE)_stats.tsv
done
}


anybelow()
{
create_dir "$OUTPUT/anybelow"
create_dir "$OUTPUT/anybelow/10x"
create_dir "$OUTPUT/anybelow/20x"

for annotated in $(find $OUTPUT/mpileup/annotated/ -name "*.tsv");
do
	./anybelow_sample.py $annotated $OUTPUT/anybelow/10x/10x_$(basename $annotated) $OUTPUT/anybelow/20x/20x_$(basename $annotated)
done

FLIST=$(echo "")
for file10x in $(find $OUTPUT/anybelow/10x/ -name "*.tsv");
do
        FLIST=$(echo "${FLIST}${file10x},")
done
FLIST=$(echo "$FLIST" | sed 's/,$//g')
./anybelow_run.py -l $FLIST -o $OUTPUT/anybelow/$(basename $BEDFILE)_10x.csv
sort $OUTPUT/anybelow/$(basename $BEDFILE)_10x.csv > $OUTPUT/anybelow/$(basename $BEDFILE)_10x_sorted.csv

FLIST=$(echo "")
for file20x in $(find $OUTPUT/anybelow/20x/ -name "*.tsv");
do
        FLIST=$(echo "${FLIST}${file20x},")
done
FLIST=$(echo "$FLIST" | sed 's/,$//g')
./anybelow_run.py -l $FLIST -o $OUTPUT/anybelow/$(basename $BEDFILE)_20x.csv
sort $OUTPUT/anybelow/$(basename $BEDFILE)_20x.csv > $OUTPUT/anybelow/$(basename $BEDFILE)_20x_sorted.csv
}


mpileup
annotate
getstats
anybelow
