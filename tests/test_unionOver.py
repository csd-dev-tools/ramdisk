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
from genericRamdiskTest import GenericRamdiskTest

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

class test_unionOver(unittest.TestCase):
    """
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
        self.message_level = "debug"

        self.libcPath = None # initial initialization

        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("darwin") and \
           not sys.platform.startswith("linux"):
            unittest.SkipTest("This is not valid on this OS")
        GenericRamdiskTest._initializeClass(message_level=self.message_level)


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
