#!/usr/bin/python -u
"""
Test unionfs functionality. 

as of 3/15/2016, only the Mac OS X platform is supported.

@author: Roy Nielsen
"""
#--- Native python libraries
import re
import os
import sys
import time
import unittest
import tempfile
import ctypes as C
from datetime import datetime

sys.path.append("../")

#--- non-native python libraries in this source tree
from ramdisk.tests.genericRamdiskTest import GenericRamdiskTest
from ramdisk.lib.loggers import Logger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.libHelperExceptions import NotValidForThisOS

#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from ramdisk.macRamdisk import RamDisk, unmount
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    from ramdisk.linuxTmpfsRamdisk import RamDisk, unmount

class test_unionOver(GenericRamdiskTest):
    """
    Test unionfs functionality of ramdisks

    @author: Roy Nielsen
    """

    @classmethod
    def setUpClass(self):
        """
        Initializer
        """
        unittest.SkipTest("Needs appropriate tests written")
        # Start timer in miliseconds
        self.test_start_time = datetime.now()

        #self.message_level = "debug"
        self.logger = Logger()

        self.libcPath = None # initial initialization

        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("darwin") and \
           not sys.platform.startswith("linux"):
            unittest.SkipTest("This is not valid on this OS")
        GenericRamdiskTest._initializeClass(self.logger)


    def setUp(self):
        """
        This method runs before each test case.

        @author: Roy Nielsen
        """
        pass


###############################################################################
##### Method Tests

    ##################################

    def test_unionOverFirstTest(self):
        """
        """
        pass

    ##################################

    def test_unionOverSecondTest(self):
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
        if unmount(self.mount):
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
