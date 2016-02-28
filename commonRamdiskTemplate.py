"""
Template for the ramdisk classes

@author: Roy Nielsen
"""
from tempfile import mkdtemp
from log_message import logMessage

###############################################################################

class RamDiskTemplate(object):
    """
    """
    def __init__(self, size=0, mountpoint="", message_level="normal"):
        """
        """
        #####
        # Version/timestamp is 
        # <YYYY><MM><DD>.<HH><MM><SS>.<microseconds>
        # in UTC time
        self.module_version = '20160224.032043.009191'
        self.message_level = message_level
        self.diskSize = size
        self.success = False
        self.myRamdiskDev = None
        if not mountpoint:
            self.getRandomizedMountpoint() 
        else:
            self.mntPoint = mountpoint 

        logMessage("disk size: " + str(self.diskSize), \
                   "debug", self.message_level)
        logMessage("volume name: " + str(self.mntPoint), \
                   "debug", self.message_level)

    ###########################################################################

    def getData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful
        """
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def printData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful.
        Also prints to the data to the console
        """
        print "Success: " + str(self.success)
        print "Mount point: " + str(self.mntPoint)
        print "Device: " + str(self.myRamdiskDev)
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def logData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful
        Also logs the data.
        """
        logMessage("Success: " + str(self.success), \
                   "debug", self.message_level)
        logMessage("Mount point: " + str(self.mntPoint), \
                   "debug", self.message_level)
        logMessage("Device: " + str(self.myRamdiskDev), \
                   "debug", self.message_level)
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def getRandomizedMountpoint(self) :
        """
        Create a randomized (secure) mount point - per python's implementation
        of mkdtemp - a way to make an unguessable directory on the system

        @author: Roy Nielsen
        """
        success = False
        try :
            self.mntPoint = mkdtemp()
        except Exception, err :
            logMessage("Exception trying to create temporary directory")
            raise err
        else :
            success = True
        logMessage("Success: " + str(success) + " in " + \
                   "__get_randomizedMountpoint: " + str(self.mntPoint), \
                   "debug", self.message_level)            
        return success

    ###########################################################################

    def unmount(self) :
        """
        Unmount the disk - same functionality as __eject on the mac

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def _format(self) :
        """
        Format the ramdisk

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def getDevice(self):
        """
        Getter for the device name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.myRamdiskDev

    ###########################################################################

    def getMountPoint(self):
        """
        Getter for the mount point name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.mntPoint

    ###########################################################################

    def setDevice(self, device=None):
        """
        Setter for the device so it can be ejected.

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        self.myRamdiskDev = device

    ###########################################################################

    def getVersion(self):
        """
        Getter for the version of the ramdisk

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.module_version

    ###########################################################################

    class NotValidForThisOS(Exception):
        """
        Meant for being thrown when an action/class being run/instanciated is not
        applicable for the running operating system.
    
        @author: Roy Nielsen
        """
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)
    
    ###########################################################################

    class BadRamdiskArguments(Exception):
        """
        Meant for being thrown when an invalid values are passed in as arguments
        to class instanciation or class methods.
    
        @author: Roy Nielsen
        """
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)

###############################################################################


def detach(device=None, message_level="normal"):
    """
    Eject the ramdisk

    Must be over-ridden to provide OS/Method specific functionality

    @author: Roy Nielsen
    """
    success = False
    return success

