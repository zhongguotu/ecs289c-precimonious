#!/usr/bin/env python

import os
import platform
import sys
from subprocess import call


"""
Transform the bitcode file with the given configuration
return  1 bitcode file is valid, threshold satisfied
        0 bitcode file is invalid, threshold not satisfied
        -1 LLVM transformation passes failure
        -3 modified bitcode file execution failure
"""


def transform(bitcodefile, configfile):

    # setting some variables
    corvettepath = os.getenv("CORVETTE_PATH")

    if platform.system() == 'Darwin':
        sharedlib = corvettepath + "/src/Passes.dylib"
    else:
        sharedlib = corvettepath + "/src/Passes.so"

    # modified bitcode file
    mbitcodefile = "m_" + sys.argv[1]
    mbitcode = open(mbitcodefile, 'w')

    # running the transformation LLVM passes
    output = open("transform.log", 'w')
    command = ['opt', '-load', sharedlib,
                      "-json-config=" + configfile,
                      "-adjust-operators", bitcodefile]
    retval = call(command, stdin=None, stdout=mbitcode, stderr=output)

    # return -1 if running LLVM passes fails
    if retval != 0:
        return -1

    # running modified bitcode
    command = ['opt', '-O2', mbitcodefile, '-o', sys.argv[1] + '_opt.bc']
    call(command, stdin=None, stdout=None, stderr=None)
    command = ['llc', sys.argv[1] + '_opt.bc', '-o', sys.argv[1] + '.s']
    call(command, stdin=None, stdout=None, stderr=None)
    command = ['clang', sys.argv[1] + '.s', '-lm', '-o', sys.argv[1] + '.out']
    call(command, stdin=None, stdout=None, stderr=None)
    command = ['./' + sys.argv[1] + '.out']
    retval = call(command, stdin=None, stdout=None, stderr=None)

    # return -3 if crashed when run
    if retval != 0:
        return -3

    output = open("sat.cov", 'r')
    firstline = output.readline()
    firstline = firstline.strip()
    if (firstline == "true"):
        return 1  # valid transformation
    else:
        return 0  # invalid transformation
