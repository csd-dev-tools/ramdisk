"""
@Notes:

Things we need to modularize:
* create
* mount
* unmount
* detach?
* format (newfs_hfs vs. diskutil)
* randomize mountpoint
* turn off journaling, for faster access

Maybe function, or other module
* Find available memory,
  - Linux - just read /proc
  - Mac - Use top's "unused" so it doesn't try to use swap
          swap would defeat the purpose.

Maybe function, method  or other module
* rsync from spinning disk to ram disk

@author: Roy Nielsen
"""

import os
import re
import sys
from tempfile import mkdtemp
from subprocess import Popen, PIPE, STDOUT

from run_commands import systemCallRetVal
from log_message import logMessage
from commonRamdiskTemplate import RamDiskTemplate

###############################################################################
class RamDisk(RamDiskTemplate) :
    """
    Class to manage a ramdisk

    utilizes commands I've used to manage ramdisks

    Size passed in must be passed in as 1Mb chunks

    @author: Roy Nielsen
    """
    def __init__(self, size=0, mountpoint="", message_level="normal") :
        """
        Constructor
        """
        super(RamDisk, self).__init__(size, mountpoint, message_level)
        self.module_version = '20160224.032043.009191'

        #####
        # Calculating the size of ramdisk in 1Mb chunks
        self.diskSize = str(int(size) * 1024 * 1024 / 512)
        self.volumename = mountpoint

        self.hdiutil = "/usr/bin/hdiutil"
        self.diskutil = "/usr/sbin/diskutil"

        if mountpoint:
            logMessage("\n\n\n\tMOUNTPOINT: " + str(mountpoint) + "\n\n\n", \
                       "debug", self.message_level)
            self.mntPoint = mountpoint
        else:
            self.mntPoint = ""

        self.myRamdiskDev = ""

        success = True

        if self.diskSize == 0 :
            success  = False
        if not self.__isMemoryAvailable() :
            success = False
            logMessage("Physical memory not available to create ramdisk.")

        if success :

            if self.volumename :
                #####
                # eventually have checking to make sure that directory doesn't already exist.
                logMessage("Attempting to use mount point of: " + \
                           str(mountpoint), "verbose", self.message_level)
                self.mntPoint = mountpoint
            else :
                logMessage("Attempting to acquire a radomized mount " + \
                           "point. . .", "verbose", self.message_level)
                if not self.getRandomizedMountpoint() :
                    success = False

            if success:
                if not self.__create():
                    success = False
                    logMessage("Create appears to have failed..", \
                               "verbose", self.message_level)
                else:
                    if not self.__mount():
                        success = False
                        logMessage("Mount appears to have failed..", \
                                   "verbose", self.message_level)
                    else:
                        if not self.__remove_journal():
                            success = False
                            logMessage("Remove journal appears to have " + \
                                       "failed..", "verbose", \
                                       self.message_level)

        self.success = success
        logMessage("Success: " + str(self.success), \
                   "verbose", self.message_level)
        logMessage("Mount point: " + str(self.mntPoint), \
                   "verbose", self.message_level)
        logMessage("Device: " + str(self.myRamdiskDev), \
                   "verbose", self.message_level)

    ###########################################################################

    def __create(self) :
        """
        Create a ramdisk device

        @author: Roy Nielsen
        """
        retval = None
        reterr = None
        success = False
        cmd = [self.hdiutil, "attach", "-nomount", "ram://" + self.diskSize]
        retval, reterr = systemCallRetVal(cmd, self.message_level)
        logMessage("retval: " + str(retval), "debug", self.message_level)
        logMessage("reterr: " + str(reterr), "debug", self.message_level)
        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + str(reterr).strip() + ")")
        else:
            self.myRamdiskDev = retval.strip()
            logMessage("Device: \"" + str(self.myRamdiskDev) + "\"", "debug", self.message_level)
            success = True
        logMessage("Success: " + str(success) + " in __create", "debug", self.message_level)            
        return success
    
    ###########################################################################

    def getData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful
        """
        logMessage("Success: " + str(self.success), "debug", self.message_level)
        logMessage("Mount point: " + str(self.mntPoint), "debug", self.message_level)
        logMessage("Device: " + str(self.myRamdiskDev), "debug", self.message_level)
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def __mount(self) :
        """
        Mount the disk

        @author: Roy Nielsen
        """
        success = False
        success = self.__attach()
        return success

    ###########################################################################

    def __attach(self):
        """
        Attach the device so it can be formatted

        @author: Roy Nielsen
        """
        success = False
        if self.__partition():
            success = True

        # eraseVolume format name device
            if self.mntPoint:
                #####
                # "Mac" unmount (not eject)
                cmd = [self.diskutil, "unmount", self.myRamdiskDev + "s1"]
                retval, reterr = systemCallRetVal(cmd, self.message_level)
                if not reterr:
                    success = True

                if success:
                    #####
                    # remount to self.mntPoint
                    cmd = [self.diskutil, "mount", "-mountPoint",
                           self.mntPoint, self.myRamdiskDev + "s1"]
                    retval, reterr = systemCallRetVal(cmd, self.message_level)
                    if not reterr:
                        success = True
            logMessage("*******************************************", "debug", self.message_level)
            logMessage(r"retval:   " + str(retval).strip(), "debug", self.message_level)
            logMessage(r"reterr:   " + str(reterr).strip(), "debug", self.message_level)
            logMessage(r"mntPoint: " + str(self.mntPoint).strip(), "debug", self.message_level)
            logMessage(r"device:   " + str(self.myRamdiskDev).strip(), "debug", self.message_level)
            logMessage("*******************************************", "debug", self.message_level)
            logMessage("Success: " + str(success) + " in __mount", "debug", self.message_level)
        return success

    ###########################################################################

    def __remove_journal(self) :
        """
        Having a journal in ramdisk makes very little sense.  Remove the journal
        after creating the ramdisk device

        cmd = ["/usr/sbin/diskutil", "disableJournal", "force", myRamdiskDev]

        using "force" doesn't work on a mounted filesystem, without it, the command
        will work on a mounted file system

        @author: Roy Nielsen
        """
        success = False
        cmd = [self.diskutil, "disableJournal", self.myRamdiskDev + "s1"]
        retval, reterr = systemCallRetVal(cmd, self.message_level)
        if not reterr:
            success = True
        logMessage("Success: " + str(success) + " in __remove_journal", "debug", self.message_level)
        return success

    ###########################################################################

    def unmount(self) :
        """
        Unmount the disk - same functionality as __eject on the mac

        @author: Roy Nielsen
        """
        success = False
        if self.eject() :
            success = True
        logMessage("Success: " + str(success) + " in unmount", "debug", self.message_level)
        return success

    ###########################################################################

    def eject(self) :
        """
        Eject the ramdisk
        Detach (on the mac) is a better solution than unmount and eject
        separately.. Besides unmounting the disk, it also stops any processes
        related to the mntPoint
        """
        success = False
        cmd = [self.hdiutil, "detach", self.myRamdiskDev]
        retval, reterr = systemCallRetVal(cmd, self.message_level)
        if not reterr:
            success = True
        logMessage("*******************************************", "debug", self.message_level)
        logMessage("retval: \"" + str(retval).strip() + "\"", "debug", self.message_level)
        logMessage("reterr: \"" + str(reterr).strip() + "\"", "debug", self.message_level)
        logMessage("*******************************************", "debug", self.message_level)
        logMessage("Success: " + str(success) + " in eject", "debug", self.message_level)
        return success

    ###########################################################################

    def _format(self) :
        """
        Format the ramdisk

        @author: Roy Nielsen
        """
        success = False
        cmd = ["/sbin/newfs_hfs", "-v", "ramdisk", self.myRamdiskDev]
        retval, reterr = systemCallRetVal(cmd, self.message_level)
        if not reterr:
            success = True
        logMessage("*******************************************", "debug", self.message_level)
        logMessage("retval: \"" + str(retval).strip() + "\"", "debug", self.message_level)
        logMessage("reterr: \"" + str(reterr).strip() + "\"", "debug", self.message_level)
        logMessage("*******************************************", "debug", self.message_level)
        logMessage("Success: " + str(success) + " in __format", "debug", self.message_level)
        return success

    ###########################################################################

    def __partition(self) :
        """
        Not implemented on the Mac

        """
        success=False
        size = int(self.diskSize)/(2*1024)
        cmd = [self.diskutil, "partitionDisk", self.myRamdiskDev, str(1),
               "MBR", "HFS+", "ramdisk", str(size) + "M"]
        retval, reterr = systemCallRetVal(cmd, self.message_level)
        if not reterr:
            success = True
        logMessage("*******************************************", "debug", self.message_level)
        logMessage("retval: \"\"\"" + str(retval).strip() + "\"\"\"", "debug", self.message_level)
        logMessage("reterr: \"" + str(reterr).strip() + "\"", "debug", self.message_level)
        logMessage("*******************************************", "debug", self.message_level)
        logMessage("Success: " + str(success) + " in __format", "debug", self.message_level)
        return success

    ###########################################################################

    def __isMemoryAvailable(self) :
        """
        Check to make sure there is plenty of memory of the size passed in
        before creating the ramdisk

        Best method to do this on the Mac is to get the output of "top -l 1"
        and re.search("unused\.$", line)

        @author: Roy Nielsen
        """
        #mem_free = psutil.phymem_usage()[2]

        #print "Memory free = " + str(mem_free)
        success = False
        self.free = 0
        cmd = ["/usr/bin/top", "-l", "1"]
        pipe = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        size = None
        freeMagnitude = None

        if pipe:
            while True:
                myout = pipe.stdout.readline()

                if myout == '' and pipe.poll() != None:
                    break

                line = myout.split()

                # Get the last item in the list
                found = line[-1]
                almost_size = line[:-1]
                size = almost_size[-1]

                logMessage("size: " + str(size), "debug", self.message_level)
                logMessage("found: " + str(found), "debug", self.message_level)

                if re.search("unused", found) or re.search("free", found):
                    break
            if size:
                sizeCompile = re.compile("(\d+)(\w+)")

                split_size = sizeCompile.search(size)
                freeNumber = split_size.group(1)
                freeMagnitude = split_size.group(2)

                logMessage("freeNumber: " + str(freeNumber), "debug", self.message_level)
                logMessage("freeMagnitude: " + str(freeMagnitude), "debug", self.message_level)

                if re.match("^\d+$", freeNumber.strip()):
                    if re.match("^\w$", freeMagnitude.strip()):
                        success = True
                        if freeMagnitude:
                            if re.search("G", freeMagnitude.strip()):
                                self.free = 1024 * int(freeNumber)
                                self.free = str(self.free)
                            elif re.search("M", freeMagnitude.strip()):
                                self.free = freeNumber
                
        return success
        
    ###########################################################################

    def getDevice(self):
        """
        Getter for the device name the ramdisk is using

        @author: Roy Nielsen
        """
        return self.myRamdiskDev

    ###########################################################################

    def setDevice(self, device=None):
        """
        Setter for the device so it can be ejected.
        
        @author: Roy Nielsen
        """
        if device:
            self.myRamdiskDev = device
        else:
            raise Exception("Problem trying to set the device..")
            
    ###########################################################################

    def getVersion(self):
        """
        Getter for the version of the ramdisk

        @author: Roy Nielsen
        """
        return self.version


###############################################################################


def detach(device=" ", message_level="normal"):
    """
    Eject the ramdisk
    Detach (on the mac) is a better solution than unmount and eject 
    separately.. Besides unmounting the disk, it also stops any processes 
    related to the mntPoint

    @author: Roy Nielsen
    """
    success = False
    if not re.match("^\s*$", device):
        cmd = ["/usr/bin/hdiutil", "detach", device]
        retval, reterr = systemCallRetVal(cmd, message_level)
        if not reterr:
            success = True

        logMessage("*******************************************", "debug", message_level)
        logMessage("retval: " + re.escape(str(retval).strip("\"")), "debug", message_level)
        logMessage("reterr: " + re.escape(str(reterr).strip("\"")), "debug", message_level)
        logMessage("*******************************************", "debug", message_level)
        logMessage("Success: " + str(success) + " in eject", "debug", message_level)
    else:
        raise Exception("Cannot eject a device with an empty name..")
    return success



