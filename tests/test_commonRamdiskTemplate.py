#!/usr/bin/python -u
"""
CommonRamdiskTemplate test.

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
from ramdisk.lib.loggers import Logger
from ramdisk.lib.loggers import LogPriority as lp

from ramdisk.lib.libHelperExceptions import NotValidForThisOS

#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from ramdisk.macRamdisk import RamDisk, detach
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    from ramdisk.linuxTmpfsRamdisk import RamDisk, unmount

class test_commonRamdiskTemplate(unittest.TestCase):
    """
    """

    @classmethod
    def setUpClass(self):
        """
        Runs once before any tests start
        """
        # Start timer in miliseconds
        self.test_start_time = datetime.now()

    ##################################

    def setUp(self):
        """
        This method runs before each test run.

        @author: Roy Nielsen
        """
        pass

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


###############################################################################
##### Functional Tests

    ##################################


###############################################################################
##### unittest Tear down
    @classmethod
    def tearDownClass(self):
        """
        Final cleanup actions...
        """
        logger = Logger()
        #####
        # capture end time
        test_end_time = datetime.now()

        #####
        # Calculate and log how long it took...
        test_time = (test_end_time - self.test_start_time)

        logger.log(lp.INFO, self.__module__ + " took " + str(test_time) + " time to complete...")

###############################################################################
