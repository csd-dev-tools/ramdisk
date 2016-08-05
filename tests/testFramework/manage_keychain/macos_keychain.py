"""
Implementation class for the individual ManageKeychain for MacOS

@author: Roy Nielsen
"""
from __future__ import absolute_import

import os

########## 
# local app libraries
from lib.run_commands import RunWith
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.manage_user.macos_user import MacOSUser


class UnsupportedSecuritySubcommand(Exception):
    """
    Meant for being thrown when a command does not support a passed in subcommand.

    @author: Roy Nielsen
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class MacOSKeychain(MacOSUser):
    """
    """
    def __init__(self, logger=False):
        """
        Initialization Method
        
        @author: Roy Nielsen
        """
        self.mgr = "/usr/bin/security"
        if not logger:
            self.logger = CyLogger()
        else:
            self.logger = logger
        self.runWith = RunWith(self.logger)

    #----------------------------------------------------------------------
    # helper methods
    #----------------------------------------------------------------------

    def validateSecurityCommand(self, command={}):
        """
        Validate that we have a properly formatted command, and the subcommand
        is valid.
        
        @param: the commandDict should be in the format below:
        
        cmd = { "set-keychain-password" : [oldPass, newPass, "'" + keychain + "'"] }
        
        where the key is the security 'subcommand' and the list is an ordered
        list of the arguments to give the subcommand.
        
        @returns: success - whether the command was successfull or not.
        
        @author: Roy Nielsen
        """
        success = False
        subcmd = []
        if not isinstance(command, dict):
            self.logger.log(lp.ERROR, "Command must be a dictionary...")
        else:
            commands = 0
            for subCommand, args in command.iteritems():
                commands += 1
                #####
                # Check to make sure only one command is in the dictionary
                if commands > 1:
                    self.logger.log(lp.ERROR, "Damn it Jim! One command at a time!!")
                    success = False
                    break
                #####
                # Check if the subcommand is a valid subcommand...
                validSubcommands = ["set-keychain-password",
                                    "unlock-keychain",
                                    "delete-keychain",
                                    "create-keychain"]
                if subCommand not in validSubcommands:
                    success = False
                    break
                #####
                # Check to make sure the key or subCommand is a string, and the value is
                # alist and args are
                if not isinstance(subCommand, basestring) or not isinstance(args, list):
                    self.logger.log(lp.ERROR, "subcommand needs to be a string, and args needs to be a list of strings")
                    success = False
                else:
                    #####
                    # Check the arguments to make sure they are all strings
                    for arg in args:
                        if not isinstance(arg, basestring):
                            self.logger.log(lp.ERROR, "Arg '" + str(arg) + "'needs to be a string...")
                            success = False
                    if success:
                        subcmd = [subCommand] + args
        return success, subcmd

    #-------------------------------------------------------------------------

    def runSecurityCommand(self, commandDict={}):
        """
        Use the passed in dictionary to create a MacOS 'security' command
        and execute it.
        
        @param: the commandDict should be in the format below:
        
        cmd = { "set-keychain-password" : [oldPass, newPass, "'" + keychain + "'"] }
        
        where the key is the security 'subcommand' and the list is an ordered
        list of the arguments to give the subcommand.
        
        @returns: success - whether the command was successfull or not.
        
        @author: Roy Nielsen
        """
        success = False
        output = ""
        error = ""
        returncode = ""
        #####
        # Make sure the command dictionary was properly formed, as well as
        # returning the formatted subcommand list
        validationSuccess, subCmd = self.validateSecurityCommand(commandDict)
        if validationSuccess:
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = [self.mgr] + subCmd
            #####
            # set up the command
            self.runWith.setCommand(cmd)
            #####
            # Run the command
            self.runWith.communicate()
            #####
            # Retrieve return values for the command execution
            output, error, returncode = self.runWith.getReturns()
            
            if not error:
                success = True
            else:
                self.logger.log(lp.INFO, "Output: " + str(output))
                self.logger.log(lp.INFO, "Error: " + str(error))
                self.logger.log(lp.INFO, "Return code: " + str(returncode))
                success = False

        return success, str(output), str(error), str(returncode)

    #----------------------------------------------------------------------
    # Subcommands
    #----------------------------------------------------------------------

    def unlockKeychain(self, passwd="", keychain=""):
        """
        Unlock the defined keychain

        @parameter: passwd - password for the keychain to unlock

        @parameter: keychain - full path to the keychain to unlock

        @note: 
        security unlock-keychain -p <passwd>

        @author: Roy Nielsen
        """
        success = False
        #####
        # Input validation for the file keychain.
        if self.isSaneFilePath(keychain) and isinstance(passwd, basestring):
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = { "unlock-keychain" : ["-p", passwd, "'" + keychain + "'"] }
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success

    #-------------------------------------------------------------------------

    def changeKeychainPassword(self, user="",
                                     oldPass=False,
                                     newPass=False,
                                     keychain=False):
        """
        Use the "security" command to set the login keychain.  If it has not
        been created, create the login keychain.

        use the following command on the Mac:
        security set-keychain-password -o <oldpassword> -p <newpassword> <file.keychain>

        Most used keychain is the login.keychain.

        @author: Roy Nielsen
        """
        success = False

        #####
        # Input validation for the username, and check the passwords to make
        # sure they are valid strings.  Check for the existence of the keychain
        if self.isSaneUserName(user) and \
           isinstance(oldPass, basestring) and \
           isinstance(newPass, basestring) and \
           self.isSaneFilePath(keychain):
            if os.path.isfile(self.getUserHomeDir(user)):
                #####
                # if a keychain isn't passed in use the user's login keychain.
                if not keychain:
                    loginKeychain = "'" + self.getUserHomeDir(user) + \
                                   "/Library/Keychains/login.keychain'"
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = { "change-keychain-password" : ["-o", oldPass, "-p", newPass,
                                                  "'" + keychain + "'"] }
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success

    #-------------------------------------------------------------------------

    def deleteKeychain(self, keychain=""):
        """
        Delete keychain
        
        @param: keychain - full path to keychain to delete, it will be removed
                           from the index as well as deleted from the 
                           filesystem.
        
        @note: the command is:

        security delete-keychain <file.keychain>

        The <file.keychain> must be the full path to the keychain.
        
        @author: Roy Nielsen
        """
        success = False
        #####
        # Input validation for the file keychain.
        if self.isSaneFilePath(keychain) and os.path.exists(keychain):
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = { "delete-keychain" : ["'" + keychain + "'"] }
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success

    #-------------------------------------------------------------------------

    def createKeychain(self, passwd="", keychain=""):
        """
        Create a keychain.
        
        @author: Roy Nielsen
        """
        success = False
        #####
        # Input validation for the file keychain.
        if self.isSaneFilePath(keychain) and isinstance(passwd, basestring):
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = { "create-keychain" : ["-p", passwd, "'" + keychain + "'"] }
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success
