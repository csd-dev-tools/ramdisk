
#####
# System Libraries
import sys


#####
# Custom package libraries.
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.CheckApplicable import CheckApplicable


class ManageUsers(object):
    """
    Class for managing groups of users
    
    @author: Roy Nielsen
    """
    def __init__(self, logger=False):
        """
        @author: Roy Nielsen
        """
        #####
        # Set up logging
        if self.logger:
            self.logger = logger
        else:
            self.logger = CyLogger()
        self.logger.log(lp.INFO, "Logger: " + str(self.logger))
        
        if sys.platform.lower() == "darwin":
            from lib.manage_users import macos_users 
            # import lib.manage_user.macos_user
            self.userMgr = macos_users.MacOSUsers(logDispatcher=self.logger)
        else:
            raise UnsupportedOSError("This operating system is not supported...")

        users = {}
        
    def getAllUsers(self):
        """
        @author: Roy Nielsen
        """
        pass

    def getUsers(self):
        """
        @author: Roy Nielsen
        """
        pass

    def getUser(self):
        """
        @author: Roy Nielsen
        """
        pass
    def getUserProperty(self):
        """
        @author: Roy Nielsen
        """
        pass

    def getUserProperties(self):
        """
        @author: Roy Nielsen
        """
        pass

    def getUsersProperty(self):
        """
        @author: Roy Nielsen
        """
        pass

    def getUsersProperties(self):
        """
        @author: Roy Nielsen
        """
        pass
