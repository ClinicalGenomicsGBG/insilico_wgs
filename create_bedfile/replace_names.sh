#!/bin/bash -l

OLD=$(echo "$1")
NEW=$(echo "$2")

echo "sed \"s/\t$OLD\t/\t$NEW\t/g\"" >> changes_made

sed -i "s/\t$OLD\t/\t$NEW\t/g" refseq_20190301_ncbiRefSeq

