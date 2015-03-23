#!/usr/bin/env python
"""
usage:
python report.py inputfilename outputfilename
"""

import sys


def main():
    """ generate report counting # of FP inst """
    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    input_file = open(inputfilename, 'r')
    data = input_file.read()
    output_file = open(outputfilename, 'w')
    output_file.write("StoreInst\n")
    output_file.write("\tFloat: " + str(data.count("call void @incrementStoreInstFloat()")) + "\n")
    output_file.write("\tDouble: " + str(data.count("call void @incrementStoreInstDouble()")) + "\n")
    output_file.write("\tLongDouble: " + str(data.count("call void @incrementStoreInstLongDouble()")) + "\n")
    output_file.write("LoadInst\n")
    output_file.write("\tFloat: " + str(data.count("call void @incrementLoadInstFloat()")) + "\n")
    output_file.write("\tDouble: " + str(data.count("call void @incrementLoadInstDouble()")) + "\n")
    output_file.write("\tLongDouble: " + str(data.count("call void @incrementLoadInstLongDouble()")) + "\n")
    output_file.write("ArithOpInst\n")
    output_file.write("\tFloat: " + str(data.count("call void @incrementArithOpInstFloat()")) + "\n")
    output_file.write("\tDouble: " + str(data.count("call void @incrementArithOpInstDouble()")) + "\n")
    output_file.write("\tLongDouble: " + str(data.count("call void @incrementArithOpInstLongDouble()")) + "\n")
    output_file.write("CmpOpInst\n")
    output_file.write("\tFloat: " + str(data.count("call void @incrementCmpOpInstFloat()")) + "\n")
    output_file.write("\tDouble: " + str(data.count("call void @incrementCmpOpInstDouble()")) + "\n")
    output_file.write("\tLongDouble: " + str(data.count("call void @incrementCmpOpInstLongDouble()")) + "\n")
    output_file.write("CastInst\n")
    output_file.write("\tTruncInst: " + str(data.count("call void @incrementFPTruncInst()")) + "\n")
    output_file.write("\tExtInst: " + str(data.count("call void @incrementFPExtInst()")) + "\n")
    input_file.close()
    output_file.close()


if __name__ == "__main__":
    main()
