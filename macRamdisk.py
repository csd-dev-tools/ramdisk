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
from subprocess import Popen, PIPE

from run_commands import RunWith
from log_message import logMessage
from commonRamdiskTemplate import RamDiskTemplate

###############################################################################
class RamDisk(RamDiskTemplate) :
    """
    Class to manage a ramdisk

    utilizes commands I've used to manage ramdisks

    Size passed in must be passed in as 1Mb chunks

    @param: size - size of the ramdisk to create - must have a value on the Mac
                   or the creation will fail.
    @param: mountpoint - where to mount the disk, if left empty, will mount
                         on locaiton created by tempfile.mkdtemp.
    @param: message_level - level at which to log.

    @author: Roy Nielsen
    """
    def __init__(self, size=0, mountpoint="", message_level="normal") :
        """
        Constructor
        """
        super(RamDisk, self).__init__(size, mountpoint, message_level)
        self.module_version = '20160225.125554.540679'
        self.message_level = message_level
        self.runWith = RunWith(self.message_level)
        #####
        # Calculating the size of ramdisk in 1Mb chunks
        self.diskSize = str(int(size) * 1024 * 1024 / 512)

        self.hdiutil = "/usr/bin/hdiutil"
        self.diskutil = "/usr/sbin/diskutil"

        #####
        # Just /dev/disk<#>
        self.myRamdiskDev = ""

        #####
        # should take the form of /dev/disk2s1, where disk 2 is the assigned
        # disk and s1 is the slice, or partition number.  While just /dev/disk2
        # is good for some things, others will need the full path to the 
        # device, such as formatting the disk.
        self.devPartition = ""

        success = False

        #####
        # Passed in disk size must have a non-default value
        if self.diskSize == 0 :
            success  = False
        #####
        # Checking to see if memory is availalbe...
        if not self.__isMemoryAvailable() :
            logMessage("Physical memory not available to create ramdisk.")
        else:
            success = True

        if success :

            #####
            # If a mountpoint is passed in, use that, otherwise, set up for a 
            # random mountpoint.
            if mountpoint:
                logMessage("\n\n\n\tMOUNTPOINT: " + str(mountpoint) + "\n\n\n",
                           "debug", self.message_level)
                self.mntPoint = mountpoint
                #####
                # eventually have checking to make sure that directory
                # doesn't already exist, and have data in it.
            else :
                #####
                # If a mountpoint is not passed in, create a randomized
                # mount point.
                logMessage("Attempting to acquire a radomized mount " + \
                           "point. . .", "verbose", self.message_level)
                if not self.getRandomizedMountpoint() :
                    success = False

            #####
            # The Mac has a more complicated method of managing ramdisks...
            if success:
                #####
                # Attempt to create the ramdisk
                if not self.__create():
                    success = False
                    logMessage("Create appears to have failed..", \
                               "verbose", self.message_level)
                else:
                    #####
                    # Ramdisk created, try mounting it.
                    if not self.__mount():
                        success = False
                        logMessage("Mount appears to have failed..", \
                                   "verbose", self.message_level)
                    else:
                        #####
                        # Filessystem journal will only slow the ramdisk down...
                        # No need to keep it as when the journal is unmounted
                        # all memory is de-allocated making it impossible to do
                        # forensics on the volume.
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
        #####
        # Create the ramdisk and attach it to a device.
        cmd = [self.hdiutil, "attach", "-nomount", "ram://" + self.diskSize]
        self.runWith.set_command(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:
            self.myRamdiskDev = retval.strip()
            logMessage("Device: \"" + str(self.myRamdiskDev) + "\"",
                       "debug", self.message_level)
            success = True
        logMessage("Success: " + str(success) + " in __create",
                   "debug", self.message_level)
        return success

    ###########################################################################

    def getData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful

        Does not print or log the data.

        @author: Roy Nielsen
        """
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def getNlogData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful

        Also logs the data.

        @author: Roy Nielsen
        """
        logMessage("Success: " + str(self.success), \
                   "debug", self.message_level)
        logMessage("Mount point: " + str(self.mntPoint), \
                   "debug", self.message_level)
        logMessage("Device: " + str(self.myRamdiskDev), \
                   "debug", self.message_level)
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def getNprintData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful
        """
        print "Success: " + str(self.success)
        print "Mount point: " + str(self.mntPoint)
        print "Device: " + str(self.myRamdiskDev)
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def __mount(self) :
        """
        Mount the disk - for the Mac, just run self.__attach

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
        #####
        # Attempt to partition the disk.
        if self.__partition():
            success = True
            #####
            # eraseVolume format name device
            if self.mntPoint:
                #####
                # "Mac" unmount (not eject)
                cmd = [self.diskutil, "unmount", self.myRamdiskDev + "s1"]
                self.runWith.set_command(cmd)
                self.runWith.communicate()
                retval, reterr, retcode = self.runWith.getNlogReturns()

                if not reterr:
                    success = True

                if success:
                    #####
                    # remount to self.mntPoint
                    cmd = [self.diskutil, "mount", "-mountPoint",
                           self.mntPoint, self.myRamdiskDev + "s1"]
                    self.runWith.set_command(cmd)
                    self.runWith.communicate()
                    retval, reterr, retcode = self.runWith.getNlogReturns()

                    if not reterr:
                        success = True
            logMessage("*******************************************",
                       "debug", self.message_level)
            self.runWith.getNlogReturns()
            self.getData()
            logMessage("*******************************************",
                       "debug", self.message_level)
            logMessage("Success: " + str(success) + " in __mount",
                       "debug", self.message_level)
        return success

    ###########################################################################

    def __remove_journal(self) :
        """
        Having a journal in ramdisk makes very little sense.  Remove the journal
        after creating the ramdisk device

        cmd = ["/usr/sbin/diskutil", "disableJournal", "force", myRamdiskDev]

        using "force" doesn't work on a mounted filesystem, without it, the
        command will work on a mounted file system

        @author: Roy Nielsen
        """
        success = False
        cmd = [self.diskutil, "disableJournal", self.myRamdiskDev + "s1"]
        self.runWith.set_command(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        logMessage("Success: " + str(success) + " in __remove_journal",
                   "debug", self.message_level)
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
        logMessage("Success: " + str(success) + " in unmount",
                   "debug", self.message_level)
        return success

    ###########################################################################

    def _unmount(self) :
        """
        Unmount in the Mac sense - ie, the device is still accessible.

        @author: Roy Nielsen
        """
        success = False
        cmd = [self.diskutil, "unmount", self.devPartition]
        self.runWith.set_command(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        return success

    ###########################################################################

    def _mount(self) :
        """
        Mount in the Mac sense - ie, mount an already accessible device to 
        a mount point.

        @author: Roy Nielsen
        """
        success = False
        cmd = [self.diskutil, "mount", "-mountPoint", self.mntPoint, self.devPartition]
        self.runWith.set_command(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        return success

    ###########################################################################

    def eject(self) :
        """
        Eject the ramdisk

        Detach (on the mac) is a better solution than unmount and eject
        separately.. Besides unmounting the disk, it also stops any processes
        related to the mntPoint
        
        @author: Roy Nielsen
        """
        success = False
        cmd = [self.hdiutil, "detach", self.myRamdiskDev]
        self.runWith.set_command(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        logMessage("*******************************************",
                   "debug", self.message_level)
        self.runWith.getNlogReturns()
        logMessage("*******************************************",
                   "debug", self.message_level)

        return success

    ###########################################################################

    def _format(self) :
        """
        Format the ramdisk

        @author: Roy Nielsen
        """
        success = False
        #####
        # Unmount (in the mac sense - the device should still be accessible)
        # Cannot format the drive unless only the device is accessible.
        success = self._unmount()
        #####
        # Format the disk (partition)
        cmd = ["/sbin/newfs_hfs", "-v", "ramdisk", self.devPartition]
        self.runWith.set_command(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        #####
        # Re-mount the disk
        self._mount()
        return success

    ###########################################################################

    def __partition(self) :
        """
        Partition the ramdisk (mac specific)

        @author: Roy Nielsen
        """
        success=False
        size = str(int(self.diskSize)/(2*1024))
        cmd = [self.diskutil, "partitionDisk", self.myRamdiskDev, str(1),
               "MBR", "HFS+", "ramdisk", str(size) + "M"]
        self.runWith.set_command(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        if success:
            #####
            # Need to get the partition device out of the output to assign to
            # self.devPartition
            for line in retval.split("\n"):
                if re.match("^Initialized (\S+)\s+", line):
                    linematch = re.match("Initialized\s+(\S+)\s+", line)
                    self.devPartition = linematch.group(1)
                    break
    
        self.runWith.getNlogReturns()

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
        found = False
        almost_size = 0
        size = 0
        self.free = 0
        line = ""
        freeMagnitude = None

        #####
        # Set up and run the command
        cmd = ["/usr/bin/top", "-l", "1"]

        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)

        while True:
            line = proc.stdout.readline().strip()
            #####
            # Split on spaces
            line = line.split()
            #####
            # Get the last item in the list
            found = line[-1]
            almost_size = line[:-1]
            size = almost_size[-1]

            found = found.strip()
            #almost_size = almost_size.strip()
            size = size.strip()

            logMessage("size: " + str(size), "debug", self.message_level)
            logMessage("found: " + str(found), "debug", self.message_level)

            if re.search("unused", found) or re.search("free", found):
                #####
                # Found the data we wanted, stop the search.
                break
        proc.kill()

        #####
        # Find the numerical value and magnitute of the ramdisk
        if size:
            sizeCompile = re.compile("(\d+)(\w+)")

            split_size = sizeCompile.search(size)
            freeNumber = split_size.group(1)
            freeMagnitude = split_size.group(2)

            if re.match("^\d+$", freeNumber.strip()):
                if re.match("^\w$", freeMagnitude.strip()):
                    if freeMagnitude:
                        #####
                        # Calculate the size of the free memory in Megabytes
                        if re.search("G", freeMagnitude.strip()):
                            self.free = 1024 * int(freeNumber)
                            self.free = str(self.free)
                        elif re.search("M", freeMagnitude.strip()):
                            self.free = freeNumber
        logMessage("free: " + str(self.free), "verbose", self.message_level)
        logMessage("Size requested: " + str(self.diskSize), "verbose", self.message_level)
        if int(self.free) > int(self.diskSize)/(2*1024):
            success = True    
        print str(self.free)
        print str(success)
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
        return self.module_version


###############################################################################

def unmount(device=" ", message_level="normal"):
    """
    On the Mac, call detach.

    @author: Roy Nielsen
    """
    detach(device, message_level)

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
    myRunWith = RunWith(message_level)
    if not re.match("^\s*$", device):
        cmd = ["/usr/bin/hdiutil", "detach", device]
        myRunWith.set_command(cmd)
        myRunWith.communicate()
        retval, reterr, retcode = myRunWith.getNlogReturns()
        if not reterr:
            success = True

        logMessage("*******************************************",
                   "debug", message_level)
        myRunWith.getNlogReturns()
        logMessage("*******************************************",
                   "debug", message_level)
    else:
        raise Exception("Cannot eject a device with an empty name..")
    return success
