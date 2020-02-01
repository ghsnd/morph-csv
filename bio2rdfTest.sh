#!/bin/bash
date=$(date "+%F-%T")
file="logs/bio2rdf/bio2rdf$date.log.txt"
echo ''> $file 
for i in 1 2 4 5 6 7 8 9 10 11 12
do
echo "QUERY: $i" >> $file
cp evaluation/bio2rdf/bio2rdf.csvw.json tmp/annotations/annotations.json
cp evaluation/bio2rdf/bio2rdf.yml tmp/annotations/mapping.yaml
cp /home/w0xter/Datasets/minBio2Rdf/* tmp/csv/
python3 Test.py  -c evaluation/bio2rdf/config-bio2rdf.json -q evaluation/bio2rdf/queries/query$i.rq >> $file
echo "----------------------------------------------------" >> $file
done