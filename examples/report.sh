#!/bin/bash
source setenv.sh

if [ ! -d "$instPath" ]; then
	mkdir "$instPath"
fi

if [ -n "$1" ]; then
	targetFile=$1
fi

if [ ! -e "$targetFile.bc" ]; then
	echo "File not found: $targetFile.bc"
	exit 1
fi

cp $targetFile.bc "$instPath"
cd "$instPath"
source $scriptPath/instrument.sh $targetFile .
llvm-dis $targetFile.bc
llvm-dis i_$targetFile.bc
python $scriptPath/report.py i_$targetFile.ll report_$targetFile.txt
cd ..