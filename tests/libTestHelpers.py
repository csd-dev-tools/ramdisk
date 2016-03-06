import os
import re
import sys
import ctypes as C
from datetime import datetime

sys.path.append("../")

from log_message import logMessage

class LibTestHelpers(object):
    """
    Holds helper methods.  DO NOT create an init

    @author: Roy Nielsen
    """

    def _initializeClass(self, initialized=None):
        """

        """
        if not initialized:
            self.getLibc()
            self.initialized = True

    ################################################
    ##### Helper Methods

    def setMessageLevel(self, msg_lvl="normal"):
        """
        Set the logging level to what is passed in.
        """
        self.message_level = msg_lvl

    def getLibc(self):
        """
        """
        self.libcPath = None # initial initialization

        self.osFamily = sys.platform.lower()

        if self.osFamily and  self.osFamily.startswith("darwin"):
            #####
            # For Mac
            self.libc = C.CDLL("/usr/lib/libc.dylib")
        if self.osFamily and  self.osFamily.startswith("linux"):
            #####
            # For Linux
            self.findLinuxLibC()
        else:
            self.libc = self._pass()

    ################################################

    def findLinuxLibC(self):
        """
        Find Linux Libc library...

        @author: Roy Nielsen
        """
        possible_paths = ["/lib/x86_64-linux-gnu/libc.so.6",
                          "/lib/i386-linux-gnu/libc.so.6"]
        for path in possible_paths:

            if os.path.exists(path):
                self.libcPath = path
                self.libc = C.CDLL(self.libcPath)
                break

    ################################################

    def _pass(self):
        """
        Filler if a library didn't load properly
        """
        pass

    ################################################

    def touch(self, fname="", message_level="normal") :
        """
        Python implementation of the touch command..

        inspiration:
        http://stackoverflow.com/questions/1158076/implement-touch-using-python

        @author: Roy Nielsen
        """
        if re.match("^\s*$", str(fname)) :
            logMessage("Cannot touch a file without a filename....", \
                       "normal", self.message_level)
        else :
            try:
                os.utime(fname, None)
            except:
                try :
                    open(fname, 'a').close()
                except Exception, err :
                    logMessage("Cannot open to touch: " + str(fname), "normal", self.message_level)

    ################################################

    def mkdirs(self, path="") :
        """
        A function to do an equivalent of "mkdir -p"
        """
        if not path :
            logMessage("Bad path...")
        else :
            if not os.path.exists(str(path)):
                try:
                    os.makedirs(str(path))
                except OSError as err1:
                    logMessage("OSError exception attempting to create directory: " + str(path))
                    logMessage("Exception: " + str(err1))
                except Exception, err2 :
                    logMessage("Unexpected Exception trying to makedirs: " + str(err2))

    ################################################

    def mkfile(self, file_path="", file_size=0, pattern="rand", block_size=512, mode=0o777):
        """
        Create a file with "file_path" and "file_size".  To be used in
        file creation benchmarking - filesystem vs ramdisk.

        @parameter: file_path - Full path to the file to create
        @parameter: file_size - Size of the file to create, in Mba
        @parameter: pattern - "rand": write a random pattern
                              "0xXX": where XX is a hex value for a byte
        @parameter: block_size - size of blocks to write in bytes
        @parameter: mode - file mode, default 0o777

        @returns: time in miliseconds the write took

        @author: Roy Nielsen
        """
        self.getLibc()
        total_time = 0
        if file_path and file_size:
            self.libc.sync()
            file_size = file_size * 1024 * 1024
            if os.path.isdir(file_path):
                tmpfile_path = os.path.join(file_path, "testfile")
            else:
                tmpfile_path = file_path
            logMessage("Writing to: " + tmpfile_path, "debug", self.message_level)
            try:
                # Get the number of blocks to create
                blocks = file_size/block_size

                # Start timer in miliseconds
                start_time = datetime.now()

                # do low level file access...
                tmpfile = os.open(tmpfile_path, os.O_WRONLY | os.O_CREAT, mode)

                # do file writes...
                for i in range(blocks):
                    tmp_buffer = os.urandom(block_size)
                    os.write(tmpfile, str(tmp_buffer))
                    os.fsync(tmpfile)
                self.libc.sync()
                os.close(tmpfile)
                self.libc.sync()
                os.unlink(tmpfile_path)
                self.libc.sync()

                # capture end time
                end_time = datetime.now()
            except Exception, err:
                logMessage("Exception trying to write temp file for "    + \
                           "benchmarking...", "normal", self.message_level)
                logMessage("Exception thrown: " + str(err), \
                           "normal", self.message_level)
                total_time = 0
            else:
                total_time = end_time - start_time
        return total_time

##################################################
