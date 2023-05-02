#!/bin/bash -l
#$ -cwd
#$ -S /bin/bash
#$ -pe mpi 1
#$ -q routine.q
#$ -l excl=1
#$ -o stdoutserrs/
#$ -e stdoutserrs/


BAM=$1
BED=$2
OUTPUT=$3

module load samtools/1.9
# Warning -- Excluding MAPQ0 will probably reveal more poor covered regions...which honestly makes sense since variantcalling is not done on MAPQ=0 reads
# And can't seq Q to 0 because then it will count overlapping pairs...

samtools mpileup -l $BED -Q 1 $BAM | cut -f1,2,4 >> $OUTPUT/$(basename $BAM)_$(basename $BED).tsv

