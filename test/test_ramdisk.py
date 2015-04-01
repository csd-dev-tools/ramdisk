#!/usr/bin/python -w
"""

@author: Roy Nielsen
"""
import re
import os
import sys
import unittest
try:
    from log_message import log_message
except:
    sys.path.append("..")
    from log_message import log_message

try:
    from macRamdisk import RamDisk, detach
except:    
    sys.path.append("..")
    from macRamdisk import RamDisk, detach

class test_ramdisk(unittest.TestCase):

    def setUp(self):
        """
        Initializer
        """
        self.setMessageLevel("normal")

        self.subdirs = ["two", "three" "one/four"]

        """
        Set up a ramdisk and use that random location as a root to test the
        filesystem functionality of what is being tested.
        """
        #Calculate size of ramdisk to make for this unit test.
        size_in_mb = 100
        ramdisk_size = size = 2 * 1024 * 500 * size_in_mb
        self.mnt_pnt_requested = ""

        self.success = False
        self.mountPoint = False
        self.ramdiskDev = False
        self.mnt_pnt_requested = False

        # get a ramdisk of appropriate size, with a secure random mountpoint
        my_ramdisk = RamDisk(str(ramdisk_size), self.mnt_pnt_requested, self.message_level)
        (self.success, self.mountPoint, self.ramdiskDev) = my_ramdisk.get_data()

        log_message("::::::::Ramdisk Mount Point: " + str(self.mountPoint), "debug", self.message_level)
        log_message("::::::::Ramdisk Device     : " + str(self.ramdiskDev), "debug", self.message_level)

        
        if not self.success:
            raise "Cannot get a ramdisk for some reason. . ."
        
###############################################################################
##### Helper Classes

    def setMessageLevel(self, msg_lvl="normal"):
        """
        Set the logging level to what is passed in.
        """
        self.message_level = msg_lvl
        

    def touch(self, fname="", message_level="normal") :
        """
        Python implementation of the touch command..
        
        inspiration: http://stackoverflow.com/questions/1158076/implement-touch-using-python
        
        @author: Roy Nielsen
        """
        if re.match("^\s*$", str(fname)) :
            log_message("Cannot touch a file without a filename....", "normal", self.message_level)
        else :
            try:
                os.utime(fname, None)
            except:
                try :
                    open(fname, 'a').close()
                except Exception, err :
                    log_message("Cannot open to touch: " + str(fname), "normal", self.message_level)


    def mkdirs(self, path="") :
        """
        A function to do an equivalent of "mkdir -p"
        """
        if not path :
            log_message("Bad path...")
        else :
            if not os.path.exists(str(path)):
                try:
                    os.makedirs(str(path))
                except OSError as err1:
                    log_message("OSError exception attempting to create directory: " + str(path))
                    log_message("Exception: " + str(err1))
                    pass
                except Exception, err2 :
                    log_message("Unexpected Exception trying to makedirs: " + str(err2))
                    pass

###############################################################################
##### Tests
        
    ##################################

    def test_files_n_dirs(self):
        """
        Should work when files exist in ramdisk.
        """
        # Do file setup for this test
        for subdir in self.subdirs:
            dirpath = self.mountPoint + "/" + subdir
            log_message("DIRPATH: : " + str(dirpath), "debug", self.message_level)
            self.mkdirs(dirpath)
            self.touch(dirpath + "/" + "test")

        # Do the tests
        for subdir in self.subdirs:
            # CANNOT use os.path.join this way.  os.path.join cannot deal with
            # absolute directories.  May work with mounting ramdisk in local
            # relative directories.
            self.assertTrue(os.path.exists(self.mountPoint + "/" + subdir + "/" +  "test"))

    ##################################

    def test_no_files_exists(self):
        """
        Test that no test files exist on ramdisk.
        """
        # Do the tests
        for subdir in self.subdirs:
            self.assertFalse(os.path.exists(self.mountPoint + "/" + subdir + "/" +  "test"))

###############################################################################
##### unittest Tear down

    def tearDown(self):
        """
        disconnect ramdisk
        """
        if detach(self.ramdiskDev, self.message_level):
            log_message(r"Successfully detached disk: " + str(self.ramdiskDev).strip(), "verbose", self.message_level)
        else:
            log_message(r"Couldn't detach disk: " + str(self.ramdiskDev).strip() + " : mntpnt: " + str(self.mntPoint))
            raise Exception(r"Cannot eject disk: " + str(self.ramdiskDev).strip() + " : mntpnt: " + str(self.mntPoint))
        
###############################################################################
