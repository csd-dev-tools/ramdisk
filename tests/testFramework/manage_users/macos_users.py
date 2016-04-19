"""
Cross platform user creation and management

Created for testing cross user testing for the ramdisk project, specifically
unionfs functionality.

@author: Roy Nielsen
"""
from __future__ import absolute_import
import re
import os
import sys
import shutil

from .manage_user import ManageUser
from .manage_user import BadUserInfoError
from lib.loggers import LogPriority as lp
from __builtin__ import False, True

class MacOSUser(ManageUser):
    """
    Class to manage users on Mac OS.

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
                 userComment="", userUid=1000, userPriGid=20,
                 userHomeDir="/tmp", logger=False):
        super(MacOSUser, self).__init__(userName, userShell,
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

    def getDscl(self, directory="", action="", dirobj="", property=""):
        """
        Using dscl to retrieve a value from the directory

        @author: Roy Nielsen
        """
        success = False
        #####
        # FIRST VALIDATE INPUT!!
        if isinstance(directory, basestring) and re.match("^[/\.][A-Za-z0-9/]*", directory):
            success = True
        else:
            success = False
        if isinstance(action, basestring) and re.match("^[-]*[a-z]+", action) and success:
            success = True
        else:
            success = False
        if isinstance(dirobj, basestring) and re.match("^[A-Za-z0=9/]+", dirobj) and success:
            success = True
        else:
            success = False
        if isinstance(property, basestring) and re.match("^[A-Za-z0-9]+", property) and success:
            success = True
        else:
            success = False
        #####
        # Now do the directory lookup.
        if success:
            cmd = [self.dscl, directory, action, object, property]

            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()

            if not reterr:
                success = True
            else:
                raise Exception("Error trying to get a value with dscl (" + \
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
        if isinstance(userName, basestring)\
           and re.match("^[A-Za-z][A-Za-z0-9]*$", userName):
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
        if self.saneUserName(user) and self.saneUserShell(shell):
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

        if self.saneUserName(user) and comment:
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

        if self.saneUserName(user) and uid:
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

        if self.saneUserName(user) and priGid:
            isSetDSL = self.setDscl(".", "-create", "/Users/" + str(user),
                                    "PrimaryGroupID", str(priGid))

            if isSetDSL:
                success = True

        return success

    def setUserHomeDir(self, user="", userHome=""):
        """
        Create a "local" home directory

        dscl . -create /Users/luser NFSHomeDirectory /Users/luser

        better yet:

        createhomedir -l -u <username>

        @author: Roy Nielsen
        """
        success = False
        #####
        # Creating a non-standard userHome is not currently permitted
        #if self.saneUserName(user) and self.saneUserHomeDir(userHome):
        if self.saneUserName(user):
            isSetDSCL = self.setDscl(".", "-create", "/Users/" + str(user),
                                     "NFSHomeDirectory", str("/Users/" + str(user)))
            if not isSetDSCL:
                success = False
            else:
                success = True

        return success

    def createHomeDirectory(self, user=""):
        """
        createhomedir -c -u luser
        
        This should use the system "User Template" for standard system user
        settings.

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
                raise Exception("Error trying to create user home (" + \
                                str(reterr).strip() + ")")
            else:
                success = True

        return success

    def addUserToGroup(self, user="", group=""):
        """
        dscl . -append /Groups/admin GroupMembership luser

        @author: Roy Nielsen
        """
        success = False

        if self.saneUserName(user) and self.saneGroupName(group):
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

        if self.saneUserName(user) and self.saneGroupName(group):
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

        if self.saneUserName(user) and isinstance(password, basestring):
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
        success = False

        if self.saneUserName(user) and isinstance(password, basestring):
            pass

        #####
        # Input validation

        #####
        # Check if login keychain exists

        #####
        # if it does not exist, create it

        #####
        # else set the login keychain password

        pass

    def rmUser(self, user=""):
        """
        dscl . delete /Users/<user>

        @author: Roy Nielsen
        """
        success = False

        if self.saneUserName(user):
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
        Remove the user home... right now only default location, but should
        look up the user home in the directory service and remove that
        specifically.
        
        @author: Roy Nielsen
        """
        success = False
        if self.saneUserName(user):
            
            #####
            #
            # ***** WARNING WILL ROBINSON *****
            #
            # Please refactor to do a lookup of the user in the directory
            # service, and use the home directory specified there..
            #
            try:
                shutil.rmtree("/Users/" + str(user))
            except IOError or OSError, err:
                self.logger.log(lp.INFO, "Exception trying to remove user home...")
                self.logger.log(lp.INFO, "Exception: " + str(err))
                raise err
            else:
                success = True

        return success

    def validateUser(self, userName=False, userShell=False, userComment=False,
                     userUid=False, userPriGid=False, userHomeDir=False):
        """
        Future functionality... validate that the passed in parameters to the
        class instanciation match.

        @author:
        """
        sane = False
        #####
        # Look up all user attributes and check that they are accurate.
        # Only check the "SANE" parameters passed in.
        if self.saneUserName(userName):
            self.userName = userName
            sane = True
        else:
            raise BadUserInfoError("Need a valid user name...")

        if self.saneUserShell(userShell) and sane:
            self.userShell = userShell
        elif not userShell:
            pass
        else:
            sane = False

        if self.saneUserComment(userComment) and sane:
            self.userComment = userComment
        elif not userComment:
            pass
        else:
            sane = False

        if self.saneUserUid(str(userUid)) and sane:
            self.userUid = self.userUid
        elif not userUid:
            pass
        else:
            sane = False

        if self.saneUserPriGid(str(userPriGid)) and sane:
            self.userUid = userUid
        elif not userPriGid:
            pass
        else:
            sane = False

        if self.saneUserHomeDir(userHomeDir) and sane:
            self.userHomeDir = userHomeDir
        elif not userHomeDir:
            pass
        else:
            sane = False

        return sane

    def getUser(self, userName=""):
        """
        """
        userInfo = False
        if self.saneUserName(userName):
            userInfo = self.getDscl(".", "read", "/Users/" + str(userName), "uid")
        else:
            raise BadUserInfoError("Need a valid user name...")

        return userInfo

    def getUserShell(self, userName=""):
        """
        """
        userShell = False
        if self.saneUserName(userName):
            userShell = self.getDscl(".", "read", "/Users/" + str(userName), "UserShell")
        else:
            raise BadUserInfoError("Need a valid user name...")

        return userShell

    def getUserComment(self, userName=""):
        """
        """
        userComment = False
        if self.saneUserName(userName):
            #####
            # Need to process the output to get the right information due to a
            # spurrious "\n" in the output
            userComment = self.getDscl(".", "read", "/Users/" + str(userName), "RealName")
        else:
            raise BadUserInfoError("Need a valid user name...")

        return userComment

    def getUserUid(self, userName=""):
        """
        """
        userUid = False
        if self.saneUserName(userName):
            userUid = self.getDscl(".", "read", "/Users/" + str(userName), "UniqueID")
            #####
            # Process to get out the right information....



        else:
            raise BadUserInfoError("Need a valid user name...")

        return userUid

    def getUserPriGid(self, userName=""):
        """
        """
        userGid = False
        if self.saneUserName(userName):
            userGid = self.getDscl(".", "read", "/Users/" + str(userName), "PrimaryGroupID")
            #####
            # Process to get out the right information....



        else:
            raise BadUserInfoError("Need a valid user name...")

        return userGid

    def getUserHomeDir(self, userName=""):
        """
        """
        userHomeDir = False
        if self.saneUserName(userName):
            userHomeDir = self.getDscl(".", "read", "/Users/" + str(userName), "NFSHomeDirectory")
            #####
            # Process to get out the right information....



        else:
            raise BadUserInfoError("Need a valid user name...")

        return userHomeDir

    def isUserInstalled(self, user=""):
        """
        Check if the user "user" is installed

        @author Roy Nielsen
        """
        if self.saneUserName(user):
            cmd = [self.dscl, ".", "-read", "/Users/" + str(user)]
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()

            if not reterr:
                success = True

        return success
