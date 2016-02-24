

from tempfile import mkdtemp
from subprocess import Popen, PIPE, STDOUT

from log_message import log_message
from run_commands import systemCallRetVal

def BadRamdiskTypeException(Exception):
    """
    Custom Exception    
    """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class RamDiskHelper(object):
    """
    Retrieve and OS specific ramdisk, and provide an interface to manage it.
    
    @author: Roy Nielsen
    """
    def __init__(self, size=0, mountpoint="", ramdiskType="loop", message_level="normal", osfamily=None):
        """
        Identify OS and instantiate an instance of a ramdisk
        """
        
        validRamdiskTypes = ["loop", ""]
        validOSFamilies = ["macos", "linux"]
        
        if not ramdiskType in validRamdiskTypes:
            raise BadRamdiskTypeException("Not a valid ramdisk type")
        
        myosfamily = self.getMyOSFamily()
        
        if myosfamily == "macos":
            from macRamdisk import RamDisk
            self.ramdisk = RamDisk(size, mountpoint, message_level)
        elif myosfamily == "linux" and ramdiskType == "loop":
            from loopRamdisk import RamDisk
            self.ramdisk == RamDisk(mountpoint, message_level)
        else:
            self.ramdisk = None
    
    def getMyOSFamily(self):
        """
        Determine what OS family the system belongs to
        
        @author: Roy Nielsen
        """ 
        pass
    
    def get_ramdisk(self):
        """
        """
        pass

    def getData(self):
        """
        Get ramdisk information from this instance if one exists..
        
        returns (self.success, str(self.mntPoint), str(self.myRamdiskDev))
                where:
                self.success = True if ramdisk creation was successful
                               False if ramdisk creation was NOT successful
                self.mountpoint = where the ramdisk is mounted on the filesystem
                self.myRamdiskDev = device the ramdisk is using
        """
        (success, mountpoint, myRamdiskDev) = self.ramdisk.getData()
        return (success, mountpoint, myRamdiskDev)
    
    def unmount(self):
        """
        """
        pass
    
    def eject(self):
        """
        """
        pass
    
    def _format(self):
        """
        """
        pass
    
    def isMemoryAvailable(self):
        """
        """
        pass
    
    def _runcmd(self, cmd, err_message):
        """
        """
        
        pass
    
    def getDevice(self):
        """
        """
        pass
    
    def getVersion(self):
        """
        """
        pass
    
def unmount(device=" ", message_level="normal"):
    """
    """
    pass

