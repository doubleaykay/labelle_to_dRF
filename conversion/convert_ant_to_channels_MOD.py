import digital_rf as drf
import numpy as np
import os
import sys
import datetime
import dateutil.parser
import argparse

"""Convert LaBelle Group data to digital_rf by reading antennas as channels"""

#get arguments from command line
def custom_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="location of file to read from")
    parser.add_argument("-o", "--output", help="location of directory to output to")
    parser.add_argument("-a", "--antennas", help="number of antennas in data")
    parser.add_argument("-c", "--chunk", help="chunk size to read in bytes")
    parser.add_argument("-r", "--rate", help="sample rate in Hz")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="Print status messages to stdout.")
    args = parser.parse_args()

    #ensure that arguments are passed
    try:
        sys.argv[1]
    except IndexError:
        print('Arguments required; use -h to see required arguments.')
        sys.exit()

#check if top level output directory exists, if not, make it
def make_dir():
    if not os.path.exists(args.output):
        if args.verbose:
            print('Output directory does not exist, making it now...')
        os.makedirs(args.output)

    #make directories to match number of antennas
    number_of_antennas = int(args.antennas)
    i = 0
    while i <= (number_of_antennas - 1):
        dir = (args.output + "/ant" + str(i))
        if not os.path.exists(dir):
            os.makedirs(dir)
        i += 1
    if args.verbose:
        print('Output directories created.')

#parameters
def parse_filename():
    #path or filename from argparse
    file = args.input
    #get filename
    path =  os.path.splitext(file)[0]
    filename = path.split("/")[path.count('/')]

def construct_dtype():
    #define data type (u2 = 2byte (16bit) unsigned integer)
    type = ('u2,' * int(args.antennas))[:-1]

def get_epoch():
    #convert start date and time into seconds since UNIX epoch
    UTstart = dateutil.parser.parse(filename.split("-")[0] + filename.split("-")[1])
    epoch = dateutil.parser.parse('1970, 1, 1')
    sec_since_epoch = int((UTstart - epoch).total_seconds())
    samples_since_epoch = sec_since_epoch * int(args.rate)

def print_verbose():
    print('Input: ' + args.input)
    print('Output: ' + args.output)
    print('Antennas: ' + args.antennas)
    print('Chunk Size: ' + args.chunk)
    print('Sample Rate in Hz: ' + args.rate)
    print('Data Type: ' + type)
    print('Path: ' + path)
    print('Filename: ' + filename)
    print('UTStart: ' + str(UTstart))
    print('Epoch: ' + str(epoch))
    print('Seconds since epoch: ' + str(sec_since_epoch))
    print('Samples since epoch: ' + str(samples_since_epoch))

def convert():
    #loop through number of antennas to write each to a channel
    b = 0
    while b <= (number_of_antennas - 1):
        #read data in chunks
        def read_in_chunks(file_object, chunk_size=int(args.chunk)):
            while True:
                data = file_object.read(chunk_size)
                if not data:
                    break
                yield data
        f = open(file, 'r')

        #define directory to write to
        dir = (args.output + "/ant" + str(b))

        #create digital_rf writer object
        writer = drf.DigitalRFWriter(
            dir, dtype=np.dtype('u2'),
            subdir_cadence_secs=3600, file_cadence_millisecs=1000,
            start_global_index=samples_since_epoch,
            sample_rate_numerator=(int(args.rate)), sample_rate_denominator=1,
            is_complex=False
        )

        #status messages if verbose flag enabled
        if args.verbose:
            print("Working directory: " + dir)
            print("Writing data for antenna " + str(b + 1))

        #pass chunks to writer object to be written
        for piece in read_in_chunks(f):
            data = np.frombuffer(piece, type, count=-1)
            writer.rf_write(data[("f" + str(b))])

        f.close()
        writer.close()

        b += 1

#Start program
custom_parser()

make_dir()

parse_filename()

construct_dtype()

get_epoch()

#confirm with user that all is fine before writing data
try:
    input("Press enter to convert data.")
except SyntaxError:
    pass

#get conversion start time
conversion_start = datetime.datetime.now()
print('Conversion start time: ' + str(conversion_start))

convert()

#get conversion end time and calculate time delta
conversion_end = datetime.datetime.now()
print('Conversion end time: ' + str(conversion_end))
print('Time elapsed:' + str(conversion_end - conversion_start))
