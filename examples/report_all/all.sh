#!/bin/bash
source ./setenv.sh

# build bitcode files
source ./compile.sh funarc
source ./compile.sh funarc_o-6
source ./compile.sh funarc_o-12
source ./compile.sh funarc_o-14
source ./compile.sh funarc_n-6
source ./compile.sh funarc_n-12
source ./compile.sh funarc_n-14

cd $buildPath/

for i in `seq 1 10`;
do
    echo $i
lli funarc.bc
lli funarc_n-14.bc
lli funarc_o-14.bc
lli funarc_n-12.bc
lli funarc_o-12.bc
lli funarc_n-6.bc
lli funarc_o-6.bc

done 


cd ..
cp $buildPath/score.cov score.cov


