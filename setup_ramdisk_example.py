#!/usr/bin/python
"""
@author: Roy Nielsen

"""
from macRamdisk import RamDisk
from log_message import logMessage
from optparse import OptionParser, SUPPRESS_HELP

parser = OptionParser(usage="\n\n%prog [options]\n\n", version="0.7.2")

size = 500 # in Megabytes
parser.add_option("-s", "--size", dest="size",
                  default=str(size),
                  help="Size of ramdisk you want to create in 1 Megabyte blocks")
parser.add_option("-m", "--mount-point", dest="mntpnt",
                  default="", 
                  help="Name of the mountpoint you want to mount to")
parser.add_option("-d", "--debug", action="store_true", dest="debug", 
                  default=0, help="Print debug messages")
parser.add_option("-v", "--verbose", action="store_true", 
                  dest="verbose", default=0, 
                  help="Print status messages")

(opts, args) = parser.parse_args()

if opts.verbose != 0:
    message_level = "verbose"
elif opts.debug != 0:
    message_level = "debug"
else:
    message_level="normal"

if opts.size:
    size = int(opts.size) # in Megabytes
mntpnt = opts.mntpnt

ramdisk = RamDisk(str(size), mntpnt, message_level)

if not ramdisk.success:
    raise Exception("Ramdisk setup failed..")

print ramdisk.getDevice()

# print "\n\n"
# print ramdisk.get_data()
