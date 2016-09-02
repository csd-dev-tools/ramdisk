"""
Helper functions, OS agnostic

@author: Roy Nielsen
"""
from __future__ import absolute_import
#--- Native python libraries
import re
import os
import sys
import ctypes
from subprocess import Popen, STDOUT, PIPE

#--- non-native python libraries in this source tree
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.run_commands import RunWith

logger = CyLogger()
run = RunWith(logger)

def getOsFamily():
    """
    Get the os name from the "uname -s" command

    @author: Roy Nielsen
    """

    operatingsystemfamily = sys.platform

    return operatingsystemfamily

##############################################################################

def get_console_user():
    """
    Get the user that owns the console on the Mac.  This user is the user that
    is logged in to the GUI.
    """
    user = False

    cmd = ["/usr/bin/stat", "-f", "'%Su'", "/dev/console"]

    try:
        retval = Popen(cmd, stdout=PIPE, stderr=STDOUT).communicate()[0]
        space_stripped = str(retval).strip()
        quote_stripped = str(space_stripped).strip("'")

    except Exception, err:
        logger.log(lp.VERBOSE, "Exception trying to get the console user...")
        logger.log(lp.VERBOSE, "Associated exception: " + str(err))
        raise err
    else:
        """
        LANL's environment has chosen the regex below as a valid match for
        usernames on the network.
        """
        if re.match("^[A-Za-z][A-Za-z1-9_]+$", quote_stripped):
            user = str(quote_stripped)
    logger.log(lp.VERBOSE, "user: " + str(user))
    
    return user

###########################################################################

def touch(filename=""):
    """
    Python implementation of the touch command..
    
    """
    if re.match("^\s*$", filename) :
        logger.log(lp.INFO, "Cannot touch a file without a filename....")
    else :
        try:
            os.utime(filename, None)
        except:
            try :
                open(filename, 'a').close()
            except Exception, err :
                logger.log(lp.INFO, "Cannot open to touch: " + str(filename))

###########################################################################


