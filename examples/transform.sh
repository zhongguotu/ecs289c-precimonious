#!/bin/bash

sharedLib=$CORVETTE_PATH"/src/Passes.so"
configFile=config_funarc.json

opt -load $sharedLib -json-config $configFile -adjust-operators funarc.bc > m_funarc.bc
opt -O2 m_funarc.bc -o funarc_opt.bc
llc funarc_opt.bc -o funarc.s
clang funarc.s -lm -o funarc.out
./funarc.out