"""
Cross platform user creation and management

Created for testing cross user testing for the ramdisk project, specifically
unionfs functionality.

@author: Roy Nielsen
"""
#from __future__ import absolute_import
import re

from lib.run_commands import RunWith
from lib.loggers import CrazyLogger
from lib.loggers import LogPriority as lp

class BadUserInfoError(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    @author: Roy Nielsen
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class ManageUser(object):
    """
    Class to manage user properties.

    @author: Roy Nielsen
    """
    def __init__(self, userName="", userShell="/bin/bash",
                       userComment="", userUid=10000, userPriGid=20,
                       userHomeDir="/tmp", logger=False):
        self.module_version = '20160225.125554.540679'

        #####
        # Set up logging
        if not logger:
            self.logger = CrazyLogger()
            self.logger.initializeLogs()
            self.logger.log(lp.INFO, "Logger: " + str(self.logger))
        else:
            self.logger = logger
            self.logger.log(lp.INFO, "Logger: " + str(self.logger))

        if userName:
            self.userName = userName
        else:
            raise BadUserInfoError("Need a user name...")

        if userShell:
            self.userShell = userShell
        else:
            raise BadUserInfoError("Need a valid user shell...")

        if userComment:
            self.userComment = userComment
        else:
            self.userComment=""

        if re.match("\d+^", str(userUid)):
            self.userUid = userUid
        else:
            raise BadUserInfoError("Need a valid user UID...")

        if userHomeDir:
            self.userHomeDir = userHomeDir
        else:
            raise BadUserInfoError("Need a user Home Directory...")

        #####
        # Initialize the RunWith helper for executing shelled out commands.
        self.runWith = RunWith(self.logger)


    def setUserName(self):
        """
        """
        pass

    def setUserShell(self, user="", shell=""):
        """
        """
        pass

    def setUserComment(self, user="", comment=""):
        """
        """
        pass

    def setUserUid(self, user="", uid=""):
        """
        """
        pass

    def setUserPriGid(self, user="", priGid=""):
        """
        """
        pass

    def setUserHomeDir(self, user="", userHome = ""):
        """
        """
        pass

    def addUserToGroup(self, user="", group=""):
        """
        """
        pass

    def setUserPassword(self, user="", password=""):
        """
        """
        pass

