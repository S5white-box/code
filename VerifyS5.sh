#!/bin/bash -x
l="${1:-5}"
s="${2:-5}"

echo "Performing the test on S5_${l}_$s"

output=S5maskVerif.ml
result=result.txt
python3 SNIS5verification.py -l $l -s $s > "$output"
python3 VerifyS5.py > testS5.py
python3 testS5.py

#Maskverif should be in PATH. /path/to/file/maskverif < S5maskVerif.ml &> "$result"
maskverif < S5maskVerif.ml &> "$result"

cat result.txt | tail -5 | head -1
cat result.txt | tail -2 | head -1
