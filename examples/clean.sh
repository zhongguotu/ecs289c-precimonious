#!/bin/bash

source setenv.sh

if [ -d "$buildPath" ]; then
	rm -rf $buildPath
fi

if [ -d "$instPath" ]; then
	rm -rf $instPath
fi


rm -f *.bc *.ll *.s *.out 
rm -f *.cov *.json *.log log.dd
rm -f report_*.txt dd2_diff_*.txt output.txt
