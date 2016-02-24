import os
import re
import sys
from tempfile import mkdtemp

from run_commands import RunWith
from log_message import logMessage
from commonRamdiskTemplate import RamDiskTemplate

###############################################################################

class RamDisk(RamDiskTemplate):
    """
    """
    def __init__(self, size=0, mountpoint="", message_level="normal"):
        """
        """
        RamDiskTemplate.__init__(self, size, mountpoint, message_level)
        self.module_version = '20160224.032043.009191'

        
    ###########################################################################

    def __create(self) :
        """
        Create a ramdisk device
        
        Must be over-ridden to provide OS/method specific ramdisk creation
        
        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def __mount(self) :
        """
        Mount the disk
        
        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def __remove_journal(self) :
        """
        Having a journal in ramdisk makes very little sense.  Remove the journal
        after creating the ramdisk device
        
        Must be over-ridden to provide OS/Method specific functionality
        
        @author: Roy Nielsen
        """
        success = False
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

    def __isMemoryAvailable(self) :
        """
        Check to make sure there is plenty of memory of the size passed in 
        before creating the ramdisk

        Must be over-ridden to provide OS/Method specific functionality
        
        @author: Roy Nielsen
        """
        #mem_free = psutil.phymem_usage()[2]

        #print "Memory free = " + str(mem_free)
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
        success = False
        return success
            
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


def unmount(device=" ", message_level="normal"):
    """
    Eject the ramdisk

    Must be over-ridden to provide OS/Method specific functionality
    
    @author: Roy Nielsen
    """
    success = False
    return success

