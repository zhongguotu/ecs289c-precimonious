#!/bin/bash

source ./setenv.sh

if [ -d "$buildPath" ]; then
	rm -rf $buildPath
fi


rm -f *.bc *.ll *.s *.out *.cov log.dd *.json
