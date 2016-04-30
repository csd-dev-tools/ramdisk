#!/usr/bin/python
"""
@author: Roy Nielsen

"""
from __future__ import absolute_import
#--- Native python libraries
import sys
from optparse import OptionParser, SUPPRESS_HELP
sys.path.append("..")
#--- non-native python libraries in this source tree
from lib.loggers import CrazyLogger
from lib.loggers import LogPriority as lp

#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from macRamdisk import RamDisk, unmount
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    from linuxTmpfsRamdisk import RamDisk, unmount
else:
    print "'" + str(sys.platform) + "' platform not supported..."

parser = OptionParser(usage="\n\n%prog [options]\n\n", version="0.7.2")

size = str(500) # in Megabytes
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
    level = Logger(level=lp.INFO)
elif opts.debug != 0:
    level = Logger(level=lp.DEBUG)
else:
    level=lp.WARNING

if opts.size:
    size = int(opts.size)  # in Megabytes
mntpnt = opts.mntpnt

logger = CrazyLogger()
logger.initializeLogs()

ramdisk = RamDisk(str(size), mntpnt)
ramdisk.logData()
ramdisk.printData()

if not ramdisk.success:
    raise Exception("Ramdisk setup failed..")

print ramdisk.getDevice()

