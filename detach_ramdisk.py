#!/usr/bin/python
"""
@author: Roy Nielsen
"""
from macRamdisk import detach
from log_message import log_message
from optparse import OptionParser, SUPPRESS_HELP

parser = OptionParser(usage="\n\n%prog [options]\n\n", version="0.7.2")

parser.add_option("-D", "--detach", dest="device", default="",
                  help="Name of the device to detach")
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

if opts.device == 0:
    raise Exception("Cannot detach a device with no name..")
else:
    device = opts.device
    
if detach(device, message_level):
    log_message(r"Successfully detached disk: " + str(device).strip(), "verbose", message_level)
else:
    log_message(r"Couldn't detach disk: " + str(device).strip())
    raise Exception(r"Cannot eject disk: " + str(device).strip())

