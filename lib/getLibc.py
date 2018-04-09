from __future__ import absolute_import

#--- Native python libraries
import os
import sys
import ctypes

##############################################################################

def getLibc(logger=False):
    """
    Acquire a reference to the system libc, initially to access the
    filesystem "sync" function.

    @returns: python reference to the C libc object, or False, if it can't
              find libc on the system.

    @author: Roy Nielsen
    """
    osFamily = sys.platform.lower().strip()
    #print "---==## OS Family: " + str(osFamily) + " #==---"

    if osFamily and  osFamily.startswith("darwin"):
        #####
        # For Mac
        try:
            libc = ctypes.CDLL("/usr/lib/libc.dylib")
        except:
            raise Exception("DAMN IT JIM!!!")

    elif osFamily and  osFamily.startswith("linux"):
        #####
        # For Linux
        possible_paths = ["/lib/x86_64-linux-gnu/libc.so.6",
                          "/lib/i386-linux-gnu/libc.so.6",
                          "/usr/lib64/libc.so.6"]
        for path in possible_paths:

            if os.path.exists(path):
                libc = ctypes.CDLL(path)
                #print "     Found libc!!!"
                break

    try:
        if libc:
            libc.sync()
            #print":::::Syncing..............."
    except:
        raise Exception("..............................Cannot Sync.")

    #print "OS Family: " + str(osFamily)

    return libc

##############################################################################
