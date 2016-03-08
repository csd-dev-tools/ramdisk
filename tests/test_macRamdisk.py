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
from log_message import logMessage
from libHelperExceptions import NotValidForThisOS

#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from macRamdisk import RamDisk, detach, unmount
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    from linuxTmpfsRamdisk import RamDisk, unmount

class test_macRamdisk(GenericRamdiskTest):
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

        #####
        # Initialize the helper class
        #self.initializeHelper = False

        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("darwin") and \
           not sys.platform.startswith("linux"):
            unittest.SkipTest("This is not valid on this OS")
        GenericRamdiskTest._initializeClass(message_level=self.message_level)
        #self._initializeClass(self.initializeHelper)
        #self.mount = self.mountPoint
        self.libcPath = None # initial initialization
        #GenericRamdiskTest.getLibc()

    ##################################

    def setUp(self):
        """
        This method runs before each test run.

        @author: Roy Nielsen
        """
        #self.getLibc()

###############################################################################
##### Method Tests

    ##################################

    def test_macRamdiskFirstTest(self):
        """
        """
        pass

    ##################################

    def test_macRamdiskSecondTest(self):
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
        unmount(self.mount)
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
