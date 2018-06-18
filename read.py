import numpy as np
import os
import sys

#parameters
#filename from command line argument
file = sys.argv[1]
#define data type (u2 = 2byte (16bit) unsigned integer)
type = np.dtype('u2')

#read data
data = np.fromfile(file, type, count=80)
#print(data[1+4])
#print(data)


def antenna(i):
    if(i<79):
        result = data[i]
        print(result)
        antenna(i+4)
    else:
        result = 0
    return result

antenna(1)