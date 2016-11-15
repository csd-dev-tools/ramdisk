"""
Implementation class for the individual ManageKeychain for MacOS

@author: Roy Nielsen
"""
from __future__ import absolute_import

import os
import re
########## 
# local app libraries
from lib.run_commands import RunWith
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.manage_user.macos_user import MacOSUser
from lib.manage_keychain.manage_keychain_template import ManageKeychainTemplate

class UnsupportedSecuritySubcommand(Exception):
    """
    Meant for being thrown when a command does not support a passed in subcommand.

    @author: Roy Nielsen
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class MacOSKeychain(MacOSUser, ManageKeychainTemplate):
    """
    """
    def __init__(self, **kwargs):
        """
        Initialization Method
        
        @author: Roy Nielsen
        """
        if 'logDispatcher' not in kwargs:
            raise ValueError("Variable 'logDispatcher' a required parameter for " + str(self.__class__.__name__))
        super(MacOSKeychain, self).__init__(**kwargs)
        #self.logger = CyLogger(debug_mode=True)
        #self.logger.initializeLogs(logdir="/tmp", filename="kch", extension_type="none", myconsole=True)
        
        self.mgr = "/usr/bin/security"
        self.userName = ""
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
            #self.logger.log(lp.DEBUG, "cmd: " + str(command))
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
                validSubcommands = ["list-keychains",
                                    "default-keychain",
                                    "login-keychain",
                                    "create-keychain",
                                    "delete-keychain",
                                    "lock-keychain",
                                    "unlock-keychain",
                                    "set-keychain-password"]
                if subCommand not in validSubcommands:
                    success = False
                    self.logger.log(lp.DEBUG, "subCommand: " + str(subCommand))
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
                    success = True
                    for arg in args:
                        if not isinstance(arg, basestring):
                            self.logger.log(lp.ERROR, "Arg '" + str(arg) + "'needs to be a string...")
                            success = False
                            break
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
        uid = os.getuid()
        #####
        # Make sure the command dictionary was properly formed, as well as
        # returning the formatted subcommand list
        validationSuccess, subCmd = self.validateSecurityCommand(commandDict)
        #self.logger.log(lp.DEBUG, "validationSuccess: " + str(validationSuccess))
        #self.logger.log(lp.DEBUG, "subCmd: " + str(subCmd))
        if validationSuccess:
            #self.logger.log(lp.DEBUG, "cmdDict: " + str(commandDict))
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
            
            if re.match("^0$", str(uid)):
                #####
                # Run the command, lift down...
                output, error, retcode = self.runWith.liftDown(self.userName)
                self.logger.log(lp.ERROR, "Took the lift down...")
                if not str(error).strip():
                    success = True
            else:
                #####
                # Run the command
                output, error, retcode = self.runWith.communicate()
                self.logger.log(lp.INFO, "DSCL cmd ran in current context..")
                
                if not str(error).strip():
                    success = True

            passfound = False
            for arg in cmd:
                if re.match('password', arg):
                    passfound = True
                    break

            if not '-p' in cmd and not passfound:
                self.logger.log(lp.DEBUG, "Output: " + str(output))
                self.logger.log(lp.DEBUG, "Error: " + str(error))
                self.logger.log(lp.DEBUG, "Return code: " + str(returncode))

        return success, str(output), str(error), str(returncode)

    #----------------------------------------------------------------------

    def setUser(self, user=""):
        """
        Setter for the class user variable..
        
        @author: Roy Nielsen
        """
        success = False
        if self.isSaneUserName(user):
            self.userName = user
            success = True
        return success

    #----------------------------------------------------------------------

    def catOne(self, subCommand="", prefDomain="", keychain="", setList=False, *args, **kwargs):
        '''
        Run a category one subcommand - a subcommand that has a options pattern of:
        
        [-h] [-d user|system|common|dynamic] [-s [keychain...]]
        
        such as list-keychains, default-keychain and login-keychain.
        
        @param: subCommand - a value inthe list of ["list-keychains",
                                                    "default-keychain",
                                                    "login-keychain"]
                                                    
        
        
        '''
        success = False
        keychain = keychain.strip()
        prefDomain = prefDomain.strip()
        
        
        validSubcommands = ["list-keychains",
                            "default-keychain",
                            "login-keychain"]
        
        if not subCommand in validSubcommands:
            return success, False, False, False
        else:
            validDomains = ['user', 'system', 'common', 'dynamic']
    
            #####
            # Input validation 
            if setList:
                
                if domain in validDomains:
                    #####
                    # Command setup - note that the keychain deliberately has quotes
                    # around it - there could be spaces in the path to the keychain,
                    # so the quotes are required to fully resolve the file path.  
                    # Note: this is done in the build of the command, rather than 
                    # the build of the variable.
                    if self.isSaneFilePath(keychain) and os.path.exists(keychain):
                        cmd = { subCommand : ["-d", prefDomain, "-s", keychain] }
                        self.logger.log(lp.DEBUG, "Setting domain: " + prefDomain + ", with keychain: " + keychain)
                    else:
                        cmd = { subCommand : ["-d", prefDomain, "-s"] }
                        self.logger.log(lp.DEBUG, "Setting domain: " + prefDomain)
                else:
                    if self.isSaneFilePath(keychain) and os.path.exists(keychain):
                        cmd = { subCommand : ["-s", keychain] }
                        self.logger.log(lp.DEBUG, "Setting keychain: " + keychain + ", with no domain")
                    else:
                        cmd = { subCommand : ["-s"] }
                        self.logger.log(lp.DEBUG, "No domain, no keychain...")
            else:  
                if domain in validDomains:
                    #####
                    # Command setup - note that the keychain deliberately has quotes
                    # around it - there could be spaces in the path to the keychain,
                    # so the quotes are required to fully resolve the file path.  
                    # Note: this is done in the build of the command, rather than 
                    # the build of the variable.
                    if self.isSaneFilePath(keychain) and os.path.exists(keychain):
                        cmd = { subCommand : ["-d", prefDomain, keychain] }
                        self.logger.log(lp.DEBUG, "Checking domain: " + prefDomain + ", with keychain: " + keychain)
                    else:
                        cmd = { subCommand : ["-d", prefDomain] }
                        self.logger.log(lp.DEBUG, "Checking domain: " + prefDomain)
                else:
                    if self.isSaneFilePath(keychain) and os.path.exists(keychain):
                        cmd = { subCommand : [keychain] }
                        self.logger.log(lp.DEBUG, "Checking keychain: " + keychain + ", with no domain")
                    else:
                        cmd = { subCommand : [] }
                        self.logger.log(lp.DEBUG, "No domain, no keychain...")
        
                success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success, stdout, stderr, retcode

    #----------------------------------------------------------------------
    # Subcommands
    #----------------------------------------------------------------------

    def listKeychains(self, keychain='', prefDomain='user', setList=False, *args, **kwargs):
        '''
        Display or manipulate the keychain search list.  Only support a single
        keychain at a time.

        @param: keychain - Keychain to list
        @param: prefDomain - user|system|common|dynamic

        @author: Roy Nielsen
        '''
        success = False
        keychain = keychain.strip()
        prefDomain = prefDomain.strip()
        
        success, output, error, retval = self.catOne("list-keychains", prefDomain, keychain, setList)
        
        return success

    #-------------------------------------------------------------------------

    def defaultKeychain(self):
        '''
        Display or set the default keychain.
        
        @param: keychain - Keychain to list
        @param: prefDomain - user|system|common|dynamic

        @author: Roy Nielsen
        '''
        success = False
        keychain = keychain.strip()
        prefDomain = prefDomain.strip()
        
        success, output, error, retval = self.catOne("default-keychain", prefDomain, keychain, setList)
        
        return success

    #-------------------------------------------------------------------------

    def loginKeychain(self):
        '''
        Display or set the login keychain.
        
        @param: keychain - Keychain to list
        @param: prefDomain - user|system|common|dynamic

        @author: Roy Nielsen
        '''
        success = False
        keychain = keychain.strip()
        prefDomain = prefDomain.strip()
        
        success, output, error, retval = self.catOne("login-keychain", prefDomain, keychain, setList)
        
        return success

    #-------------------------------------------------------------------------

    def createKeychain(self, passwd="", keychain="", *args, **kwargs):
        """
        Create a keychain.

        @author: Roy Nielsen
        """
        success = False
        passwd = passwd.strip()
        keychain = keychain.strip()
        #####
        # Input validation for the file keychain.
        if self.isSaneFilePath(keychain) and isinstance(passwd, basestring):
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = { "create-keychain" : ["-p", passwd, keychain] }
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success

    #-------------------------------------------------------------------------

    def deleteKeychain(self, keychain="", *args, **kwargs):
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
        keychain = keychain.strip()
        #####
        # Input validation for the file keychain.
        if self.isSaneFilePath(keychain) and os.path.exists(keychain):
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = { "delete-keychain" : [keychain] }
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success

    #-------------------------------------------------------------------------

    def lockKeychain(self, keychain="", all=False):
        """
        Lock the defined keychain

        @parameter: keychain - full path to the keychain to unlock

        @note: 
        security unlock-keychain -p <passwd>

        @author: Roy Nielsen
        """
        success = False
        keychain = keychain.strip()
        #####
        # Input validation for the file keychain.
        if self.isSaneFilePath(keychain):
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            if all:
                cmd = { "unlock-keychain" : ["-a", keychain] }
            else:
                cmd = { "unlock-keychain" : [keychain] }
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success

    #-------------------------------------------------------------------------

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
        keychain = keychain.strip()
        passwd = passwd.strip()
        #####
        # Input validation for the file keychain.
        if self.isSaneFilePath(keychain) and isinstance(passwd, basestring):
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = { "unlock-keychain" : ["-p", passwd, keychain] }
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
        user = user.strip()
        oldPass = oldPass.strip()
        newPass = newPass.strip()
        keychain = keychain.strip()

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
                    loginKeychain = self.getUserHomeDir(user) + \
                                   "/Library/Keychains/login.keychain"
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = { "set-keychain-password" : ["-o", oldPass, "-p", newPass,
                                                  keychain] }
            self.logger.log(lp.DEBUG, "cmd: " + str(cmd))
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)
            self.logger.log(lp.DEBUG, "stdout: " + str(stdout))
            self.logger.log(lp.DEBUG, "stderr: " + str(stderr))
            self.logger.log(lp.DEBUG, "retcode: " + str(retcode))

        return success

    #-------------------------------------------------------------------------

    def showKeychainInfo(self, keychain, *args, **kwargs):
        '''
        Show the settings for a keychain.

        @param: keychain - keychain to acquire information about
        
        @author: Roy Nielsen
        '''
        success = False
        stdout = False
        keychain = keychain.strip()
        #####
        # Input validation for the file keychain.
        if self.isSaneFilePath(keychain) and os.path.exists(keychain):
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            cmd = { "show-keychain-info" : [keychain] }
            self.logger.log(lp.DEBUG, "cmd: " + str(cmd))
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success, stdout

    #-------------------------------------------------------------------------

    def dumpKeychain(self, *args, **kwargs):
        '''
        Dump the contents of one or more keychains.

        @Note: No parameters currently supported, will dump all information.

        @author: Roy Nielsen
        '''
        success = False
        stdout = False
        #####
        # Command setup - note that the keychain deliberately has quotes
        # around it - there could be spaces in the path to the keychain,
        # so the quotes are required to fully resolve the file path.  
        # Note: this is done in the build of the command, rather than 
        # the build of the variable.
        cmd = { "dump-keychain" : [] }
        self.logger.log(lp.DEBUG, "cmd: " + str(cmd))
        success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success, stdout

    #-------------------------------------------------------------------------

    def findCertificate(self, name='', keychain='', *args, **kwargs):
        '''
        Find a certificate item.  Search based on 'name', currently finds all,
        matches, printing output in PEM format.

        @param: name - search string
        @param: keychain - keychain to search, default = search list

        @author: Roy Nielsen
        '''
        success = False
        stdout = False
        name = name.strip()
        keychain = keychain.strip()
        
        if not name or not isinstance(name, basestring):
            return success, stdout
        else:
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            if self.isSaneFilePath(keychain) and os.path.exists(keychain):
                cmd = { "find-certificate" : ["-a", "-c", name, "-p", keychain] }
            else:
                cmd = { "find-certificate" : ["-a", "-c", name, "-p"] }
            self.logger.log(lp.DEBUG, "cmd: " + str(cmd))
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success, stdout

    #-------------------------------------------------------------------------

    def findIdentity(self, policy='', sstring='', keychain='', *args, **kwargs):
        '''
        Find an identity (certificate + private key).  Only shows valid identities.

        @param: policy - value in a list of validProperties in this method
        @param: sstring - search string
        @param: keychain - (optional) - keychain to search, otherwise the search list.

        @author: Roy Nielsen
        '''
        success = False
        stdout = False
        name = name.strip()
        keychain = keychain.strip()
        
        validPolicies = ["basic", "ssl-client", "ssl-server", "smime", "eap",
                         "ipsec", "ichat", "codesigning", "sys-default", 
                         "sys-kerberos-kdc"]
        
        if not policy or not isinstance(policy, basestring) or \
           not sstring or not isinstance(sstring, basestring) or \
           not policy in validPolicies:
            return success, stdout
        else:
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            if self.isSaneFilePath(keychain) and os.path.exists(keychain):
                cmd = { "find-identity" : ["-p", policy, "-s", sstring, "-v", keychain] }
            else:
                cmd = { "find-identity" : ["-p", policy, "-s", sstring, "-v"] }
            self.logger.log(lp.DEBUG, "cmd: " + str(cmd))
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success, stdout

    #-------------------------------------------------------------------------

    def error(self, ecode='', *args, **kwargs):
        '''
        Display descrip6tive message for the given error code(s).

        @param: Error code to acquire information about.

        @author: Roy Nielsen
        '''
        success = False
        stdout = False
        ecode = ecode.strip()

        if not ecode or not isinstance(ecode, basestring):
            return success, stdout
        else:
            #####
            # Command setup - note that the keychain deliberately has quotes
            # around it - there could be spaces in the path to the keychain,
            # so the quotes are required to fully resolve the file path.  
            # Note: this is done in the build of the command, rather than 
            # the build of the variable.
            if keychain and isinstance(keychain, basestring):
                cmd = { "find-identity" : ["-p", policy, "-s", sstring, "-v", keychain] }
            else:
                cmd = { "find-identity" : ["-p", policy, "-s", sstring, "-v"] }
            self.logger.log(lp.DEBUG, "cmd: " + str(cmd))
            success, stdout, stderr, retcode = self.runSecurityCommand(cmd)

        return success, stdout
