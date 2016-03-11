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

from genericRamdiskTest import GenericRamdiskTest
from loggers import Logger
from loggers import LogPriority as lp
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
    from linuxTmpfsRamdisk import RamDisk, unmount

class test_linuxTmpfsRamdisk(GenericRamdiskTest):
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

        self.libcPath = None # initial initialization

        logger = Logger()

        #####
        # Initialize the helper class
        self.initializeHelper = False

        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("linux"):
            unittest.SkipTest("This is not valid on this OS")
        GenericRamdiskTest._initializeClass(logger)

    def setUp(self):
        """
        This method runs before each test run.

        @author: Roy Nielsen
        """
        pass


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
##### unittest Tear down
    @classmethod
    def tearDownClass(self):
        """
        disconnect ramdisk
        """
        if  unmount(self.mount):
            self.logger.log(lp.INFO, r"Successfully detached disk: " + \
                       str(self.my_ramdisk.mntPoint).strip())
        else:
            self.logger.log(lp.WARNING, r"Couldn't detach disk: " + \
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

        self.logger.log(lp.INFO, self.__module__ + " took " + str(test_time) + \
                  " time to complete...")

###############################################################################