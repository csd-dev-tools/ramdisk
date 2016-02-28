#!/usr/bin/python -u
"""

@author: Roy Nielsen
"""
import re
import os
import sys
import time
import unittest
import tempfile
import ctypes as C
from datetime import datetime


sys.path.append("../")

from log_message import logMessage
from libHelperExceptions import NotValidForThisOS

#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from macRamdisk import RamDisk, detach
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    from linuxTmpfsRamdisk import RamDisk, detach

class test_ramdisk(unittest.TestCase):
    """
    """

    @classmethod
    def setUpClass(self):
        """
        Initializer
        """
        # Start timer in miliseconds
        self.test_start_time = datetime.now()

        #self.message_level = "debug"
        self.message_level = "debug"

        self.libcPath = None # initial initialization

        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("darwin") and \
           not sys.platform.startswith("linux"):
            unittest.SkipTest("This is not valid on this OS")

        self.subdirs = ["two", "three" "one/four"]

        """
        Set up a ramdisk and use that random location as a root to test the
        filesystem functionality of what is being tested.
        """
        #Calculate size of ramdisk to make for this unit test.
        size_in_mb = 1800
        ramdisk_size = size = size_in_mb
        self.mnt_pnt_requested = ""

        self.success = False
        self.mountPoint = False
        self.ramdiskDev = False
        self.mnt_pnt_requested = False

        # get a ramdisk of appropriate size, with a secure random mountpoint
        self.my_ramdisk = RamDisk(str(ramdisk_size),
                                  self.mnt_pnt_requested,
                                  self.message_level)
        (self.success, self.mountPoint, self.ramdiskDev) = self.my_ramdisk.getData()

        logMessage("::::::::Ramdisk Mount Point: " + str(self.mountPoint), \
                   "debug", self.message_level)
        logMessage("::::::::Ramdisk Device     : " + str(self.ramdiskDev), \
                   "debug", self.message_level)

        if not self.success:
            raise IOError("Cannot get a ramdisk for some reason. . .")

        #####
        # Create a temp location on disk to run benchmark tests against
        self.fs_dir = tempfile.mkdtemp()

    def setUp(self):
        """
        This method runs before each test run.

        @author: Roy Nielsen
        """
        self.libcPath = None # initial initialization
        #####
        # setting up to call ctypes to do a filesystem sync
        if sys.platform.startswith("darwin"):
            #####
            # For Mac
            self.libc = C.CDLL("/usr/lib/libc.dylib")
        elif sys.platform.startswith("linux"):
            #####
            # For Linux
            self.findLinuxLibC()
            self.libc = C.CDLL(self.libcPath)
        else:
            self.libc = self._pass()

        

###############################################################################
##### Helper Classes

    def setMessageLevel(self, msg_lvl="normal"):
        """
        Set the logging level to what is passed in.
        """
        self.message_level = msg_lvl

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
                break

    def _pass(self):
        """
        Filler if a library didn't load properly
        """
        pass

    def touch(self, fname="", message_level="normal") :
        """
        Python implementation of the touch command..

        inspiration: http://stackoverflow.com/questions/1158076/implement-touch-using-python

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

    def format_ramdisk(self):
        """
        Format Ramdisk
        """
        self.my_ramdisk._format()

###############################################################################
##### Method Tests

    ##################################

    def test_init(self):
        """
        """
        pass

    ##################################

    def test_get_data(self):
        """
        """
        pass

    ##################################

    def test_getRandomizedMountpoint(self):
        """
        """
        pass

    ##################################

    def test_create(self):
        """
        """
        pass

    ##################################

    def test_mount(self):
        """
        """
        pass

    ##################################

    def test_attach(self):
        """
        """
        pass

    ##################################

    def test_remove_journal(self):
        """
        """
        pass

    ##################################

    def test_unmount(self):
        """
        """
        pass

    ##################################

    def test_eject(self):
        """
        """
        pass

    ##################################

    def test_format(self):
        """
        """
        pass

    ##################################

    def test_partition(self):
        """
        """
        pass

    ##################################

    def test_isMemoryAvailable(self):
        """
        """
        pass

    ##################################

    def test_runcmd(self):
        """
        """
        pass

    ##################################

    def test_getDevice(self):
        """
        """
        pass

    ##################################

    def test_setDevice(self):
        """
        """
        pass

    ##################################

    def test_getVersion(self):
        """
        """
        pass

    ##################################

    def test_detach(self):
        """
        """
        pass

###############################################################################
##### Functional Tests

    ##################################

    def test_files_n_dirs(self):
        """
        Should work when files exist in ramdisk.
        """
        # Do file setup for this test
        for subdir in self.subdirs:
            dirpath = self.mountPoint + "/" + subdir
            logMessage("DIRPATH: : " + str(dirpath), "debug", self.message_level)
            self.mkdirs(dirpath)
            self.touch(dirpath + "/" + "test")

        # Do the tests
        for subdir in self.subdirs:
            # CANNOT use os.path.join this way.  os.path.join cannot deal with
            # absolute directories.  May work with mounting ramdisk in local
            # relative directories.
            self.assertTrue(os.path.exists(self.mountPoint + "/" + subdir + "/" +  "test"))

    ##################################

    def test_four_file_sizes(self):
        """
        Test file creation of various sizes, ramdisk vs. filesystem
        """
        #####
        # Clean up the ramdisk
        self.my_ramdisk._format()
        #####
        # 100Mb file size
        oneHundred = 100
        #####
        # 100Mb file size
        twoHundred = 200
        #####
        # 500Mb file size
        fiveHundred = 500
        #####
        # 1Gb file size
        oneGig = 1000

        my_fs_array = [oneHundred, twoHundred, fiveHundred, oneGig]
        time.sleep(1)
        for file_size in my_fs_array:
            logMessage("testfile size: " + str(file_size), "debug", self.message_level)
            #####
            # Create filesystem file and capture the time it takes...
            fs_time = self.mkfile(os.path.join(self.fs_dir, "testfile"), file_size)
            logMessage("fs_time: " + str(fs_time), "debug", self.message_level)
            time.sleep(1)

            #####
            # get the time it takes to create the file in ramdisk...
            ram_time = self.mkfile(os.path.join(self.mountPoint, "testfile"), file_size)
            logMessage("ram_time: " + str(ram_time), "debug", self.message_level)
            time.sleep(1)

            speed = fs_time - ram_time
            logMessage("ramdisk: " + str(speed) + " faster...", "debug", self.message_level)

            self.assertTrue((fs_time - ram_time).days>-1)


    def test_many_small_files_creation(self):
        """
        """
        #####
        # Clean up the ramdisk
        self.my_ramdisk._format()
        #####
        #
        ramdisk_starttime = datetime.now()
        for i in range(1000):
            self.mkfile(os.path.join(self.mountPoint, "testfile" + str(i)), 1)
        ramdisk_endtime = datetime.now()

        rtime = ramdisk_endtime - ramdisk_starttime

        fs_starttime = datetime.now()
        for i in range(1000):
            self.mkfile(os.path.join(self.fs_dir, "testfile" + str(i)), 1)
        fsdisk_endtime = datetime.now()

        fstime = fsdisk_endtime - fs_starttime

        self.assertTrue((fstime - rtime).days > -11)

###############################################################################
##### unittest Tear down
    @classmethod
    def tearDownClass(self):
        """
        disconnect ramdisk
        """
        if detach(self.ramdiskDev, self.message_level):
            logMessage(r"Successfully detached disk: " + \
                       str(self.ramdiskDev).strip(), \
                       "verbose", self.message_level)
        else:
            logMessage(r"Couldn't detach disk: " + \
                       str(self.ramdiskDev).strip() + " : mntpnt: " + \
                       str(self.my_ramdisk.mntPoint))
            raise Exception(r"Cannot eject disk: " + \
                            str(self.ramdiskDev).strip() + \
                            " : mntpnt: " + str(self.my_ramdisk.mntPoint))
        #####
        # capture end time
        test_end_time = datetime.now()

        #####
        # Calculate and log how long it took...
        test_time = (test_end_time - self.test_start_time)

        logMessage(self.__module__ + " took " + str(test_time) + \
                  " time to complete...",
                  "normal", self.message_level)

###############################################################################
