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

from libTestHelpers import LibTestHelpers
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

class test_linuxTmpfsRamdisk(unittest.TestCase, LibTestHelpers):
    """
    """

    @classmethod
    def setUpClass(self):
        """
        Initializer
        """
        unittest.SkipTest("Appropriate tests need to be written...")
        # Start timer in miliseconds
        self.test_start_time = datetime.now()

        #self.message_level = "debug"
        self.message_level = "debug"

        self.libcPath = None # initial initialization

        #####
        # Initialize the helper class
        self.initializeHelper = False

        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("linux"):
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
        self._initializeClass(self.initializeHelper)


###############################################################################
##### Helper Classes

    def format_ramdisk(self):
        """
        Format Ramdisk
        """
        self.my_ramdisk._format()

###############################################################################
##### Method Tests

    def test_linuxTmpfsRamdiskFirstTest(self):
        """
        """
        pass

    ##################################

    def test_linuxTmpfsRamdiskSecondTest(self):
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

        for file_size in my_fs_array:
            logMessage("testfile size: " + str(file_size), "debug", self.message_level)
            #####
            # Create filesystem file and capture the time it takes...
            fs_time = self.mkfile(os.path.join(self.fs_dir, "testfile"), file_size)
            logMessage("fs_time: " + str(fs_time), "debug", self.message_level)

            #####
            # get the time it takes to create the file in ramdisk...
            ram_time = self.mkfile(os.path.join(self.mountPoint, "testfile"), file_size)
            logMessage("ram_time: " + str(ram_time), "debug", self.message_level)

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
        if self.my_ramdisk.unmount():
            logMessage(r"Successfully detached disk: " + \
                       str(self.my_ramdisk.mntPoint).strip(), \
                       "verbose", self.message_level)
        else:
            logMessage(r"Couldn't detach disk: " + \
                       str(self.my_ramdisk.myRamdiskDev).strip() + \
                       " : mntpnt: " + str(self.my_ramdisk.mntPoint))
            raise Exception(r"Cannot eject disk: " + \
                            str(self.my_ramdisk.myRamdiskDev).strip() + \
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
