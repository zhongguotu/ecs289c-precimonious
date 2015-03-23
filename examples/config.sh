#!/bin/bash
source setenv.sh

# generate configuration files
source $scriptPath/pconfig_op.sh $targetFile
source $scriptPath/search_op.sh $targetFile