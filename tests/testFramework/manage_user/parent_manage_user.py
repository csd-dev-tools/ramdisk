"""
Cross platform user creation and management

Created for testing cross user testing for the ramdisk project, specifically
unionfs functionality.

@author: Roy Nielsen
"""
#from __future__ import absolute_import
import re

from lib.run_commands import RunWith
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp


class BadUserInfoError(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    @author: Roy Nielsen
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ParentManageUser(object):
    """
    Class to manage user properties.

    @author: Roy Nielsen
    """
    def __init__(self, logger=False, userName="", userShell="/bin/bash",
                       userComment="", userUid=10000, userPriGid=20,
                       userHomeDir="/tmp"):
        self.module_version = '20160225.125554.540679'

        #####
        # Set up logging
        self.logger = logger
        #####
        # THIS IS A LIBRARY, SO LOGS SHOULD BE INITIALIZED ELSEWHERE...
        # self.logger.initializeLogs()
        self.logger.log(lp.INFO, "Logger: " + str(self.logger))

        #####
        # Initialize the RunWith helper for executing shelled out commands.
        self.runWith = RunWith(self.logger)

    def isSaneUserName(self, userName=""):
        """
        """
        sane = False
        if userName and isinstance(userName, basestring):
            if re.match("^[A-Za-z][A-Za-z0-9]*", userName):
                sane = True
        return sane

    def isSaneGroupName(self, groupName=""):
        """
        """
        sane = False
        if groupName and isinstance(groupName, basestring):
            if re.match("^[A-Za-z][A-Za-z0-9]*", groupName):
                sane = True
        return sane

    def isSaneUserShell(self, userShell=""):
        """
        """
        sane = False
        if userShell and isinstance(userShell, basestring):
            if re.match("^[A-Za-z/][A-Za-z0-9/]*", userShell):
                sane = True
        return sane

    def isSaneUserComment(self, userComment=""):
        """
        """
        sane = False
        if userComment and isinstance(userComment, basestring):
            if re.match("^[A-Za-z][A-Za-z0-9]*", userComment):
                sane = True
        return sane

    def isSaneUserUid(self, userUid=""):
        """
        """
        sane = False
        if userUid and isinstance(userUid, [basestring, int]):
            if re.match("^\d+", str(userUid)):
                sane = True
        return sane

    def isSaneUserPriGid(self, userPriGid=1000):
        """
        """
        sane = False
        if userPriGid and isinstance(userPriGid, [basestring, int]):
            if re.match("^\d+", str(userPriGid)):
                sane = True
        return sane

    def isSaneUserHomeDir(self, userHomeDir=""):
        """
        """
        sane = False
        if userHomeDir and isinstance(userHomeDir, basestring):
            if re.match("^[A-Za-z/][A-Za-z0-9/]*", userHomeDir):
                sane = True
        return sane

    def setUserName(self, userName=""):
        """
        """
        sane = False
        if self.isSaneUserName(userName):
            sane = True
            self.userName = userName
        return sane

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

    def authenticate(self, user="", password=""):
        """
        """
        pass
