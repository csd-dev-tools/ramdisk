"""
Cross platform user creation and management

Created for testing cross user testing for the ramdisk project, specifically
unionfs functionality.

@author: Roy Nielsen
"""
from __future__ import absolute_import
from .manage_user import ManageUser
import re
import os
import sys
import shutil

from lib.loggers import LogPriority as lp

class MacOSXUser(ManageUser):
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

        if not userUid or self.uidTaken(userUid):
            self.findUniqueUid()
        else:
            pass

        pass

    def createStandardUser(self, userName, password):
        """
        Creates a user that has the "next" uid in line to be used, then puts
        in in a group of the same id.  Uses /bin/bash as the standard shell.
        The userComment is left empty.  Primary use is managing a user
        during test automation, when requiring a "user" context.
        
        It does not set a login keychain password as that is created on first
        login to the GUI.

        @author: Roy Nielsen
        """
        self.createBasicUser(userName)
        newUserID = self.findUniqueUid()
        newUserGID = newUserID
        self.setUserUid(userName, newUserID)
        self.setUserPriGid(userName, newUserID)
        self.setUserHomeDir(userName)
        self.setUserShell(userName, "/bin/bash")
        self.setUserPassword(userName, password)
        #####
        # Don't need to set the user login keychain password as it should be
        # created on first login.

    def setDscl(self, directory=".", action="", object="", property="", value=""):
        """
        Using dscl to set a value in a directory...

        @author: Roy Nielsen
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
        success = False
        if directory and action and object and property and value:
            cmd = [self.dscl, directory, action, object, property]

            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()

            if not reterr:
                success = True
            else:
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
        maxUserID = 0
        newUserID = 0
        userList = self.getDscl(".", "-list", "/Users", "UniqueID")

        #####
        # Sort the list, add one to the highest value and return that
        # value
        for user in str(userList).split("\n"):
            if int(user.split()[1]) > maxUserID:
                maxUserID = int(user.split()[1])

        newUserID = str(int(maxUserID + 1))

        return newUserID

    def uidTaken(self, uid):
        """
        See if the UID requested has been taken.  Only approve uid's over 1k
           $ dscl . -list /Users UniqueID

        @author: Roy Nielsen
        """
        uidList = []
        success = False
        userList = self.getDscl(".", "-list", "/Users", "UniqueID")

        #####
        # Sort the list, add one to the highest value and return that
        # value
        for user in str(userList).split("\n"):
            uidList.append(str(user.split()[1]))

        if str(uid) in uidList:
            success = True

        return success

    def createBasicUser(self, userName=""):
        """
        Create a username with just a moniker.  Allow the system to take care of
        the rest.
        
        Only allow usernames with letters and numbers.
        
        On the MacOS platform, all other steps must also be done.
        
        @author: Roy Nielsen
        """
        success = False
        if userName and re.match("^[A-Za-z0-9]*$"):
            cmd = [self.dscl, ".", "-create", "/Users/" + str(userName)]
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()

            if reterr:
                success = False
                raise Exception("Error trying to set a value with dscl (" + \
                                str(reterr).strip() + ")")
        return success
            

    def setUserShell(self, user="", shell=""):
        """
        dscl . -create /Users/luser UserShell /bin/bash

        @author: Roy Nielsen
        """
        success = False
        if user and shell:
            isSetDSL = self.setDscl(".", "-create", "/Users/" + str(user),
                                   "UserShell", str(shell))
            if isSetDSL:
                success = True

        return success

    def setUserComment(self, user="", comment=""):
        """
        dscl . -create /Users/luser RealName "Real A. Name"

        @author: Roy Nielsen
        """
        success = False

        if user and comment:
            isSetDSL = self.setDscl(".", "-create", "/Users/" + str(user),
                                   "RealName", str(comment))
            if isSetDSL:
                success = True

        return success

    def setUserUid(self, user="", uid=""):
        """
        dscl . -create /Users/luser UniqueID "503"

        @author: Roy Nielsen
        """
        success = False

        if user and uid:
            isSetDSL = self.setDscl(".", "-create", "/Users/" + str(user),
                                   "UniqueID", str(uid))

            if isSetDSL:
                success = True

        return success

    def setUserPriGid(self, user="", priGid=""):
        """
        dscl . -create /Users/luser PrimaryGroupID 20

        @author: Roy Nielsen
        """
        success = False

        if user and priGid:
            isSetDSL = self.setDscl(".", "-create", "/Users/" + str(user),
                                    "PrimaryGroupID", str(priGid))

            if isSetDSL:
                success = True

        return success

    def setUserHomeDir(self, user=""):
        """
        Create a "local" home directory

        dscl . -create /Users/luser NFSHomeDirectory /Users/luser

        better yet:

        createhomedir -l -u <username>

        @author: Roy Nielsen
        """
        success = False

        if user:
            isSetDSCL = self.setDscl(".", "-create", "/Users/" + str(user),
                                     "NFSHomeDirectory", str("/Users/" + str(user)))
            if not isSetDSCL:
                success = False
            else:
                success = True

        return success

    def addUserToGroup(self, user="", group=""):
        """
        dscl . -append /Groups/admin GroupMembership luser

        @author: Roy Nielsen
        """
        success = False

        if user and group:
            isSetDSCL = self.setDscl(".", "-append", "/Groups/" + str(group),
                                     "GroupMembership", str(user))
        if not isSetDSCL:
            success = False
        else:
            success = True

        return success

    def rmUserFromGroup(self, user="", group=""):
        """
        """
        success = False

        if user and group:
            isSetDSCL = self.setDscl(".", "-delete", "/Groups/" + str(group),
                                     "GroupMembership", str(user))
        if not isSetDSCL:
            success = False
        else:
            success = True

        return success

    def setUserPassword(self, user="", password=""):
        """
        dscl . -passwd /Users/luser password

        @author: Roy Nielsen
        """
        success = False

        if user and password:
            isSetDSCL = self.setDscl("."", -passwd", "/Users/" + str(user),
                                     password)

        if not isSetDSCL:
            success = False
        else:
            success = True

        return success

    def setUserLoginKeychainPassword(self, user="", password=""):
        """
        Use the "security" command to set the login keychain.  If it has not
        been created, create the login keychain.

        Needs research.. Not sure if a sudo'd admin can use the security
        command to change another user's keychain password...

        possibly:
        security set-keychain-password -o oldpassword -p newpassword file.keychain

        where file.keychain is the default login.keychain of another user?

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

        pass

    def createHomeDirectory(self, user=""):
        """
        createhomedir -c -u luser

        @author: Roy Nielsen
        """
        success = False

        if user:
            cmd = ["/usr/sbin/createhomedir", "-c", " -u", + str(user)]
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

    def rmUser(self, user=""):
        """
        dscl . delete /Users/<user>

        @author: Roy Nielsen
        """
        success = False

        if user:
            cmd = [self.dscl, ".", "-delete", "/Users/" + str(user)]
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

    def rmUserHome(self, user=""):
        """

        """
        success = False
        if user:
            try:
                shutil.rmtree("/Users/" + str(user))
            except IOError or OSError, err:
                self.logger.log(lp.INFO, "Exception trying to remove user home...")
                self.logger.log(lp.INFO, "Exception: " + str(err))
                raise err
            else:
                success = True

        return success

    def validateUser(self):
        """
        Future functionality... validate that the passed in parameters to the
        class instanciation match.

        @author:
        """
        pass

    def isUserInstalled(self, user=""):
        """
        Check if the user "user" is installed

        @author Roy Nielsen
        """
        success = False

        if user:
            cmd = [self.dscl, ".", "-read", "/Users/" + str(user)]
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()

            if not reterr:
                success = True

        return success

