#!/bin/bash
source ./setenv.sh

if [ ! -d "$buildPath" ]; then
	mkdir "$buildPath"
fi

clang -emit-llvm -I$loggingPath -c $1.c -o $buildPath/temp_$1.bc
clang -emit-llvm -c $loggingPath/cov_checker.c -o $buildPath/cov_checker.bc
clang -emit-llvm -c $loggingPath/cov_serializer.c -o $buildPath/cov_serializer.bc
clang -emit-llvm -c $loggingPath/cov_log.c -o $buildPath/cov_log.bc
clang -emit-llvm -c $loggingPath/cov_rand.c -o $buildPath/cov_rand.bc
clang -emit-llvm -c $loggingPath/timers.c -o $buildPath/timers.bc
# generate $1.bc
llvm-link -o $buildPath/$1.bc $buildPath/temp_$1.bc $buildPath/cov_checker.bc $buildPath/cov_serializer.bc $buildPath/cov_log.bc $buildPath/cov_rand.bc $buildPath/timers.bc
