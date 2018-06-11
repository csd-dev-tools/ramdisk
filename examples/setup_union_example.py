#!/usr/bin/python
"""
@author: Roy Nielsen


"""
#--- Native python libraries
import os
import sys
from optparse import OptionParser, SUPPRESS_HELP
sys.path.append("../..")
#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp

#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from ramdisk.macRamdisk import RamDisk
    from ramdisk.macRamdisk import detach
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    from ramdisk.linuxTmpfsRamdisk import RamDisk
    from ramdisk.linuxTmpfsRamdisk import umount

parser = OptionParser(usage="\n\n%prog [options]\n\n", version="0.7.2")

size = str(500) # in Megabytes
parser.add_option("-s", "--size", dest="size",
                  default=str(size),
                  help="Size of ramdisk you want to create in 1 Megabyte blocks")
parser.add_option("-o", "--overlay-point", dest="mntpnt",
                  default="",
                  help="Name of the location you want to put the ramdisk " + \
                  "on top of.")
parser.add_option("-d", "--debug", action="store_true", dest="debug",
                  default=0, help="Print debug messages")
parser.add_option("-v", "--verbose", action="store_true",
                  dest="verbose", default=False,
                  help="Print status messages")

(opts, args) = parser.parse_args()

if opts.verbose:
    level = CyLogger(level=lp.INFO)
elif opts.debug:
    level = CyLogger(level=lp.DEBUG)
else:
    level=lp.WARNING

if opts.size:
    size = int(opts.size) # in Megabytes
else:
    size = str(512)

if opts.mntpnt:
    mntpnt = opts.mntpnt
else:
    mntpnt = "uniontest"

if not os.path.exists(mntpnt):
    os.makedirs(mntpnt)

logger = CyLogger(level=level)
logger.initializeLogs()

ramdisk = RamDisk(size=size)
ramdisk.getNlogData()
ramdisk.getNprintData()

ramdisk.unionOver(mntpnt)

ramdisk.getNprintData()

if not ramdisk.success:
    raise Exception("Ramdisk setup failed..")

print ramdisk.getDevice()



print "\n\n"
print ramdisk.getData()
