#!/bin/bash
source ./setenv.sh

# build bitcode files
source ./compile.sh

# generate configuration files
source ./config.sh

# generate floating-point instructions report
source ./report.sh

# run the target program
#lli $targetFile.bc

# run dd2 algorithm
source ./search.sh

# generate floating-point instructions report
# of transformed bitcode
source ./report.sh $targetFile.bc_opt

