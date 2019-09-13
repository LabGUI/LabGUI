#!/bin/bash

# go to root directory
cd ..


arguments=("--in-place") #,"--aggressive")

echo autopep8 ${arguments[@]} FILE

directories=($(find . -type d | grep -v venv| grep -v git | grep -v __ | grep -v build)) # only works cuz no files should have spaces

i=0

# cycle through each directory

for d in "${directories[@]}"
do
	echo "pepping directory $d"

	for f in $(ls $d | grep '\.py$')
	do
		autopep8 ${arguments[@]} $d/$f >/dev/null
		if [[ $? -ne 0 ]]; then
			echo "Error in $d/$f"
			exit
		else
			i=$((i+1))
		fi
	done
done




echo "$i files pep'd"
