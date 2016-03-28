"""
Cross platform user creation and management

Created for testing cross user testing for the ramdisk project, specifically
unionfs functionality.

@author: Roy Nielsen
"""
from __future__ import absolute_import

from lib.run_commands import RunWith
from lib.loggers import CrazyLogger
from lib.loggers import LogPriority as lp
from tests.testFramework.manage_users.manage_users_template import ManageUsersTemplate

class MacOSXUser(ManagerUsersTemplate):
    """
    Class to manage user properties.

    @method findUniqueUid
    @method setUserShell
    @method setUserComment
    @method setUserUid
    @method setUserPriGid
    @method setUserHomeDir
    @method addUserToGroup
    @method rmUserFromGroup
    @method setUserPassword
    @method setUserLoginKeychainPassword
    @method createHomeDirectory
    @method rmUser
    @method rmUserHome

    @author: Roy Nielsen
    """
    def __init__(self, userName="", userShell="/bin/bash",
                       userComment="", userUid=0, userPriGid=20,
                       userHomeDir="/tmp", logger=False):
        super(MacOSXUser, self).__init__(userName, userShell,
                                         userComment, userUid, userPriGid,
                                         userHomeDir, logger)
        self.module_version = '20160225.125554.540679'
        self.dscl = "/usr/bin/dscl"

        if not userName:
            raise ""

        if not userUid or self.uidTaken():
            self.findUniqueUid()
        else:
            pass

        pass

    def setDscl(self, directory="", action="", object="", property="", value=""):
        """
        Using dscl to set a value in a directory...
        
        @auther: Roy Nielsen
        """
        success = False
        if directory and action and object and property and value:
            cmd = [self.dscl, directory, action, object, property, value]

            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()
    
            if reterr:
                success = False
                raise Exception("Error trying to set a value with dscl (" + \
                                str(reterr).strip() + ")")
            else:
                success = True

        return success                

    def getDscl(self, directory="", action="", object="", property="", value=""):
        """
        Using dscl to retrieve a value from the directory
        
        @author: Roy Nielsen
        """
        retval = False
        if directory and action and object and property and value:
            cmd = [self.dscl, directory, action, object, property]

            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()
    
            if reterr:
                success = False
                raise Exception("Error trying to set a value with dscl (" + \
                                str(reterr).strip() + ")")
        return retval

    def findUniqueUid(self):
        """
        We need to make sure to find an unused uid (unique ID) for the user,
           $ dscl . -list /Users UniqueID
        will list all the existing users, an unused number above 500 is good.

        @author: Roy Nielsen
        """
        success = False
        cmd = [self.dscl, ".", "-list", "/Users", "UniqueID"]

        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:
            #####
            # Sort the list, add one to the highest value and return that
            # value
            pass

    def uidTaken(self):
        """
        See if the UID requested has been taken.  Only approve uid's over 1k
           $ dscl . -list /Users UniqueID

        @author: Roy Nielsen
        """
        success = False
        cmd = [self.dscl, ".", "-list", "/Users", "UniqueID"]

        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def setUserShell(self, user="", shell=""):
        """
        dscl . -create /Users/luser UserShell /bin/bash

        @author: Roy Nielsen
        """
        success = False
        if user and shell:
            cmd = [self.dscl, "-create", "/Users/" + str(user),
                   "UserShell", str(shell)]

            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()
    
            if reterr:
                success = False
                raise Exception("Error trying to create ramdisk(" + \
                                str(reterr).strip() + ")")
            else:
                success = True

        return success                

    def setUserComment(self, user="", comment=""):
        """
        dscl . -create /Users/luser RealName "Real A. Name"

        @author: Roy Nielsen
        """
        success = False

        if user and comment:
            cmd = [self.dscl, ".", "-create", "/Users/" + str(user),
                   "RealName", str(comment)]
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()
    
            if reterr:
                success = False
                raise Exception("Error trying to create ramdisk(" + \
                                str(reterr).strip() + ")")
            else:
                success = True
            
        return success

    def setUserUid(self, user="", uid=""):
        """
        dscl . -create /Users/luser UniqueID "503"

        @author: Roy Nielsen
        """
        success = False

        if user and uid:
            cmd = [self.dscl, ".", "-create", "/Users/" + str(user),
                   "UniqueID", str(uid)]
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()
    
            if reterr:
                success = False
                raise Exception("Error trying to create ramdisk(" + \
                                str(reterr).strip() + ")")
            else:
                success = True
            
        return success

    def setUserPriGid(self, user="", priGid=""):
        """
        dscl . -create /Users/luser PrimaryGroupID 20

        @author: Roy Nielsen
        """
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def setUserHomeDir(self, user="", userHome = ""):
        """
        dscl . -create /Users/luser NFSHomeDirectory /Users/luser
        """
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def addUserToGroup(self, user="", group=""):
        """
        dscl . -append /Groups/admin GroupMembership luser

        @author: Roy Nielsen
        """
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def rmUserFromGroup(self):
        """
        """
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def setUserPassword(self, user="", password=""):
        """
        dscl . -passwd /Users/luser password

        @author: Roy Nielsen
        """
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def setUserLoginKeychainPassword(self, user="", password=""):
        """
        Use the "security" command to set the login keychain.  If it has not
        been created, create the login keychain.

        @author: Roy Nielsen
        """
        self.sec = "/usr/bin/security"

        #####
        # Input validation

        #####
        # Check if login keychain exists

        #####
        # if it does not exist, create it

        #####
        # else set the login keychain password

        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def createHomeDirectory(self, user=""):
        """
        createhomedir -c -u luser

        @author: Roy Nielsen
        """
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def rmUser(self, user=""):
        """

        """
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def rmUserHome(self, user=""):
        """

        """
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        if reterr:
            success = False
            raise Exception("Error trying to create ramdisk(" + \
                            str(reterr).strip() + ")")
        else:

    def validateUser(self):
        """

        """
        pass
