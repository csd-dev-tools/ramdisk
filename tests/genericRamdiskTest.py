"""
Generic ramdisk test, with helper functions. Inherited by other tests.

@author: Roy Nielsen
"""
#--- Native python libraries
from __future__ import absolute_import
import os
import re
import sys
import tempfile
import unittest
import ctypes
from datetime import datetime
#sys.path.append("../")
#--- non-native python libraries in this source tree
from lib.loggers import CrazyLogger
from lib.loggers import LogPriority as lp

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

class GenericRamdiskTest(unittest.TestCase):
    """
    Holds helper methods.  DO NOT create an init

    Inspiration for using classmethod:
    http://simeonfranklin.com/testing2.pdf

    @author: Roy Nielsen
    """
    @classmethod
    def setUpClass(self):
        """
        """
        self.getLibc(sys.platform.lower())
        self.subdirs = ["two", "three" "one/four"]
        self.logger = CrazyLogger()
        self.logger.log(lp.CRITICAL, "Logger initialized............................")

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
        self.my_ramdisk = RamDisk(size=str(ramdisk_size), logger=self.logger)
        (self.success, self.mountPoint, self.ramdiskDev) = self.my_ramdisk.getData()

        self.mount = self.mountPoint

        self.logger.log(lp.INFO, "::::::::Ramdisk Mount Point: " + str(self.mountPoint))
        self.logger.log(lp.INFO, "::::::::Ramdisk Device     : " + str(self.ramdiskDev))

        if not self.success:
            raise IOError("Cannot get a ramdisk for some reason. . .")

        #####
        # Create a temp location on disk to run benchmark tests against
        self.fs_dir = tempfile.mkdtemp()

        # Start timer in miliseconds
        self.test_start_time = datetime.now()

        self.setUpInstanceSpecifics()

    @classmethod
    def setUpInstanceSpecifics(self):
        """
        Call the child class setUpClass initializer, if possible..

        Here to be over-ridden by a child class.

        @author: Roy Nielsen
        """
        pass

    ################################################
    ##### Helper Methods

    @classmethod
    def getLibc(self, osfamily=""):
        """
        """
        print "---==## OS Family: " + str(osfamily) + " #==---"
        self.libcPath = None  # initial initialization

        self.osFamily = osfamily

        if self.osFamily and  self.osFamily.startswith("darwin"):
            #####
            # For Mac
            try:
                self.libc = ctypes.CDLL("/usr/lib/libc.dylib")
            except:
                raise Exception("DAMN IT JIM!!!")
            else:
                print "Loading Mac dylib......................................"
        elif self.osFamily and  self.osFamily.startswith("linux"):
            #####
            # For Linux
            possible_paths = ["/lib/x86_64-linux-gnu/libc.so.6",
                              "/lib/i386-linux-gnu/libc.so.6",
                              "/usr/lib64/libc.so.6"]
            for path in possible_paths:

                if os.path.exists(path):
                    self.libcPath = path
                    self.libc = ctypes.CDLL(self.libcPath)
                    print "     Found libc!!!"
                    break
        else:
            self.libc = self._pass()

        try:
            self.libc.sync()
            print":::::Syncing..............."
        except:
            raise Exception("..............................Cannot Sync.")

        print "OS Family: " + str(self.osFamily)

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
                self.libc = ctypes.CDLL(self.libcPath)
                break

    ################################################
    @classmethod
    def _pass(self):
        """
        Filler if a library didn't load properly
        """
        pass

    ################################################

    def touch(self, fname="", message_level="normal"):
        """
        Python implementation of the touch command..

        inspiration:
        http://stackoverflow.com/questions/1158076/implement-touch-using-python

        @author: Roy Nielsen
        """
        if re.match("^\s*$", str(fname)):
            self.logger.log(lp.WARNING, "Cannot touch a file without a filename....")
        else:
            try:
                os.utime(fname, None)
            except:
                try:
                    open(fname, 'a').close()
                except Exception, err:
                    self.logger.log(lp.WARNING, "Cannot open to touch: " + str(fname))

    ################################################

    def mkdirs(self, path=""):
        """
        A function to do an equivalent of "mkdir -p"
        """
        if not path:
            self.logger.log(lp.WARNING, "Bad path...")
        else:
            if not os.path.exists(str(path)):
                try:
                    os.makedirs(str(path))
                except OSError as err1:
                    self.logger.log(lp.WARNING, "OSError exception attempting to create directory: " + str(path))
                    self.logger.log(lp.WARNING, "Exception: " + str(err1))
                except Exception, err2:
                    self.logger.log(lp.WARNING, "Unexpected Exception trying to makedirs: " + str(err2))

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
        total_time = 0
        if file_path and file_size:
            self.libc.sync()
            file_size = file_size * 1024 * 1024
            if os.path.isdir(file_path):
                tmpfile_path = os.path.join(file_path, "testfile")
            else:
                tmpfile_path = file_path
            self.logger.log(lp.DEBUG, "Writing to: " + tmpfile_path)
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
                self.logger.log(lp.WARNING, "Exception trying to write temp file for "  + \
                                "benchmarking...")
                self.logger.log(lp.WARNING, "Exception thrown: " + str(err))
                total_time = 0
            else:
                total_time = end_time - start_time
        return total_time

    ################################################

    def _unloadRamdisk(self):
        """
        """
        if self.my_ramdisk.unmount():
            self.logger.log(lp.INFO, r"Successfully detached disk: " + \
                       str(self.my_ramdisk.mntPoint).strip())
        else:
            self.logger.log(lp.WARNING, r"Couldn't detach disk: " + \
                       str(self.my_ramdisk.myRamdiskDev).strip() + \
                       " : mntpnt: " + str(self.my_ramdisk.mntPoint))
            raise Exception(r"Cannot eject disk: " + \
                            str(self.my_ramdisk.myRamdiskDev).strip() + \
                            " : mntpnt: " + str(self.my_ramdisk.mntPoint))

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
            self.logger.log(lp.DEBUG, "DIRPATH: : " + str(dirpath))
            self.mkdirs(dirpath)
            self.touch(dirpath + "/" + "test")

        # Do the tests
        for subdir in self.subdirs:
            # CANNOT use os.path.join this way.  os.path.join cannot deal with
            # absolute directories.  May work with mounting ramdisk in local
            # relative directories.
            self.assertTrue(os.path.exists(self.mountPoint + "/" + subdir + "/" +  "test"), "Problem with ramdisk...")

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
            self.logger.log(lp.INFO, "testfile size: " + str(file_size))
            #####
            # Create filesystem file and capture the time it takes...
            fs_time = self.mkfile(os.path.join(self.fs_dir, "testfile"), file_size)
            self.logger.log(lp.INFO, "fs_time: " + str(fs_time))

            #####
            # get the time it takes to create the file in ramdisk...
            ram_time = self.mkfile(os.path.join(self.mountPoint, "testfile"), file_size)
            self.logger.log(lp.INFO, "ram_time: " + str(ram_time))

            speed = fs_time - ram_time
            self.logger.log(lp.INFO, "ramdisk: " + str(speed) + " faster...")

            self.assertTrue((fs_time - ram_time).days > -1, "Problem with ramdisk...")

    ##################################

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

        self.assertTrue((fstime - rtime).days > -1, "Problem with ramdisk...")

    ##################################

    @classmethod
    def tearDownInstanceSpecifics(self):
        """
        Skeleton method in case a child class wants/needs to override it.

        @author: Roy Nielsen
        """
        pass

    @classmethod
    def tearDownClass(self):
        """
        """
        self.tearDownInstanceSpecifics()
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
