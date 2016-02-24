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
        self.version = "0.9.4"

        self.message_level = message_level
        self.volumename = mountpoint
        self.diskSize = size
        self.success = False
        self.myRamdiskDev = None
        self.mntPoint = None

        logMessage("disk size: " + str(self.diskSize), \
                   "debug", self.message_level)
        logMessage("volume name: " + str(self.volumename), \
                   "debug", self.message_level)

    ###########################################################################

    def getData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful
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
        success = False
        return success

###############################################################################


def detach(device=None, message_level="normal"):
    """
    Eject the ramdisk

    Must be over-ridden to provide OS/Method specific functionality

    @author: Roy Nielsen
    """
    success = False
    return success

