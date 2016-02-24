"""
Library for running executables from the command line in different ways

Inspiration for some of the below found on the internet.

@author: Roy Nielsen
"""
import os
import re
import pty
import time
import types
import select
import termios
import threading
from subprocess import Popen, PIPE

from log_message import logMessage

class RunWith(object):
    """
    Class that will run commands in various ways.

    @method setCommand(self, command=[])
    @method communicate(self)
    @method wait(self)
    @method timeout(self, seconds=0)
    @method runAs(self, user="", password="")
    @method runAsWithSudo(self, user="", password="")
    @method getStdout(self)
    @method getStderr(self)
    @method getReturnCode(self)

    @author: Roy Nielsen
    """
    def __init__(self, message_level="normal"):
        self.message_level = message_level
        self.command = None
        self.stdout = None
        self.stderr = None
        self.module_version = '20160224.172830.506697'
        self.returncode = None
        self.printcmd = None
        self.myshell = None

    def set_command(self, command, myshell=False):
        """
        initialize a command to run

        @author: Roy Nielsen
        """
        if command:
            self.command = command
        #####
        # Handle Popen's shell, or "myshell"...
        if isinstance(self.command, types.ListType) :
            self.printcmd = " ".join(self.command)
        if isinstance(self.command, types.StringTypes) :
            self.printcmd = self.command

        self.myshell = myshell

    ##############################################################################

    def getStdout(self):
        """
        Getter for the standard output of the last command.

        @author: Roy Nielsen
        """
        return self.stdout

    ##############################################################################

    def getStderr(self):
        """
        Getter for the standard error of the last command.

        @author: Roy Nielsen
        """
        return self.stderr

    ##############################################################################

    def getReturnCode(self):
        """
        Getter for the return code of the last command.

        @author: Roy Nielsen
        """
        return self.returncode

    ##############################################################################

    def communicate(self) :
        """
        Use the subprocess module to execute a command, returning
        the output of the command

        @author: Roy Nielsen
        """
        if self.command:
            try :
                proc = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=self.myshell)

                proc.communicate()

            except Exception, err :
                logMessage("system_call_retval - Unexpected Exception: "  + \
                           str(err)  + " command: " + self.printcmd, "normal", \
                           self.message_level)
                raise err
            else :
                logMessage(self.printcmd + \
                            " Returned with error/returncode: " + \
                            str(proc.returncode), \
                            "debug", \
                            self.message_level)
                proc.stdout.close()
            finally:
                logMessage("Done with command: " + self.printcmd, \
                            "verbose", \
                            self.message_level)
                self.stdout = proc.stdout
                self.stderr = proc.stderr
                self.returncode = proc.returncode
        else :
            logMessage("Cannot run a command that is empty...", "normal", self.message_level)
            self.stdout = None
            self.stderr = None
            self.returncode = None

    ##############################################################################

    def wait(self) :
        """
        Use subprocess to call a command and wait until it is finished before
        moving on...

        @author: Roy Nielsen
        """
        if self.command :
            try:
                proc = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=self.myshell)
                proc.wait()
            except Exception, err:
                logMessage("system_call_retval - Unexpected Exception: "  + \
                           str(err)  + " command: " + self.printcmd, "normal", \
                           self.message_level)
                raise err
            else :
                logMessage(self.printcmd + \
                            " Returned with error/returncode: " + \
                            str(proc.returncode), \
                            "debug", \
                            self.message_level)
                proc.stdout.close()
            finally:
                logMessage("Done with command: " + self.printcmd, \
                            "verbose", \
                            self.message_level)
                self.stdout = proc.stdout
                self.stderr = proc.stderr
                self.returncode = proc.returncode
        else :
            logMessage("Cannot run a command that is empty...", "normal", self.message_level)
            self.stdout = None
            self.stderr = None
            self.returncode = None

    ##############################################################################

    def killProc(self, proc, timeout) :
        """
        Support function for the "runWithTimeout" function below

        @author: Roy Nielsen
        """
        timeout["value"] = True
        proc.kill()

    ##############################################################################

    def timeout(self, timout_sec) :
        """
        Run a command with a timeout - return:
        Returncode of the process
        stdout of the process
        stderr of the process
        timout - True if the command timed out
                 False if the command completed successfully

        @author: Roy Nielsen
        """
        if self.command:
            try:
                proc = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=self.myshell)

                timeout = {"value" : False}
                timer = threading.Timer(timout_sec, self.kill_proc, [proc, timeout])
                timer.start()
                self.stdout, self.stderr = proc.communicate()
                timer.cancel()
                self.returncode = proc.returncode
            except Exception, err:
                logMessage("system_call_retval - Unexpected Exception: "  + \
                           str(err)  + " command: " + self.printcmd, "normal", \
                           self.message_level)
                raise err
            else :
                logMessage(self.printcmd + \
                            " Returned with error/returncode: " + \
                            str(proc.returncode), \
                            "debug", \
                            self.message_level)
                proc.stdout.close()
            finally:
                logMessage("Done with command: " + self.printcmd, \
                            "verbose", \
                            self.message_level)
        else :
            logMessage("Cannot run a command that is empty...", "normal", self.message_level)
            self.stdout = None
            self.stderr = None
            self.returncode = None

        return timeout["value"]

    ##############################################################################

    def runAs(self, user="", password="") :
        """
        Use pexpect to run "su" to run a command as another user...

        Required parameters: user, password, command

        inspiration from: http://stackoverflow.com/questions/12419198/python-subprocess-readlines-hangs

        @author: Roy Nielsen
        """
        if re.match("^\s*$", user) or \
           re.match("^\s*$", password) or \
           not self.command :
            logMessage("Cannot pass in empty parameters...", "normal", self.message_level)
            logMessage("user = \"" + str(user) + "\"", "normal", self.message_level)
            logMessage("check password...", "normal", self.message_level)
            logMessage("command = \"" + str(self.command) + "\"", "normal", self.message_level)
            return(255)
        else :
            output = ""
            internal_command = ["/usr/bin/su", "-", str(user), "-c"]

            if isinstance(self.command, list) :
                internal_command.append(" ".join(self.command))
                #log_message("Trying to execute: \"" + " ".join(internal_command) + "\"", \
                #            "verbose", message_level)
            elif isinstance(self.command, basestring) :
                internal_command.append(self.command)
                #log_message("Trying to execute: \"" + str(internal_command) + "\"", \
                #            "verbose", message_level)

            (master, slave) = pty.openpty()

            proc = Popen(internal_command, stdin=slave, stdout=slave, stderr=slave, close_fds=True)

            prompt = os.read(master, 10)

            if re.match("^Password:", str(prompt)) :
                os.write(master, password + "\n")
                line = os.read(master, 512)
                output = output + line
                while True :
                    r,w,e = select.select([master], [], [], 0) # timeout of 0 means "poll"
                    if r :
                        line = os.read(master, 512)
                        #####
                        # Warning, uncomment at your own risk - several programs
                        # print empty lines that will cause this to break and
                        # the output will be all goofed up.
                        #if not line :
                        #    break
                        #print output.rstrip()
                        output = output + line
                    elif proc.poll() is not None :
                        break
                os.close(master)
                os.close(slave)
                proc.wait()
                self.stdout = proc.stdout
                self.stderr = proc.stderr
                self.returncode = proc.returncode
            else:
                self.stdout = None
                self.stderr = None
                self.returncode = None
            #print output.strip()
            output = output.strip()
            #log_message("Leaving runAs with: \"" + str(output) + "\"", "debug", message_level)
            return output

    ##############################################################################

    def getecho (self, fileDescriptor):
        """This returns the terminal echo mode. This returns True if echo is
        on or False if echo is off. Child applications that are expecting you
        to enter a password often set ECHO False. See waitnoecho().

        Borrowed from pexpect - acceptable to license
        """
        attr = termios.tcgetattr(fileDescriptor)
        if attr[3] & termios.ECHO:
            return True
        return False

    ##############################################################################

    def waitnoecho (self, fileDescriptor, timeout=3):
        """This waits until the terminal ECHO flag is set False. This returns
        True if the echo mode is off. This returns False if the ECHO flag was
        not set False before the timeout. This can be used to detect when the
        child is waiting for a password. Usually a child application will turn
        off echo mode when it is waiting for the user to enter a password. For
        example, instead of expecting the "password:" prompt you can wait for
        the child to set ECHO off::

            see below in runAsWithSudo

        If timeout is None or negative, then this method to block forever until ECHO
        flag is False.

        Borrowed from pexpect - acceptable to license
        """
        if timeout is not None and timeout > 0:
            end_time = time.time() + timeout 
        while True:
            if not self.getecho(fileDescriptor):
                return True
            if timeout < 0 and timeout is not None:
                return False
            if timeout is not None:
                timeout = end_time - time.time()
            time.sleep(0.1)
    
    ##############################################################################

    def runAsWithSudo(self, user="", password="") :
        """
        Use pty method to run "su" to run a command as another user...

        Required parameters: user, password, command

        @author: Roy Nielsen
        """
        logMessage("Starting runAsWithSudo: ", "debug", self.message_level)
        logMessage("\tuser: \"" + str(user) + "\"", "debug", self.message_level)
        logMessage("\tcmd : \"" + str(self.command) + "\"", "debug", self.message_level)
        logMessage("\tmessage_level: \"" + str(self.message_level) + "\"", "normal", self.message_level)
        if re.match("^\s+$", user) or re.match("^\s+$", password) or \
           not user or not password or \
           not self.command :
            logMessage("Cannot pass in empty parameters...", "normal", self.message_level)
            logMessage("user = \"" + str(user) + "\"", "normal", self.message_level)
            logMessage("check password...", "normal", self.message_level)
            logMessage("command = \"" + str(self.command) + "\"", "normal", self.message_level)
            return(255)
        else :
            output = ""

            internal_command = ["/usr/bin/su", str("-"), str(user).strip(), str("-c")]

            if isinstance(self.command, list) :
                cmd = []
                for i in range(len(self.command)):
                    try:
                        cmd.append(str(self.command[i].decode('utf-8')))
                    except UnicodeDecodeError :
                        cmd.append(str(self.command[i]))

                internal_command.append(str("/usr/bin/sudo -E -S -s '" + " ".join(cmd) + "'"))
                #log_message("Trying to execute: \"" + " ".join(internal_command) + "\"", \
                #            "verbose", message_level)
                #print "Trying to execute: \"" + " ".join(internal_command) + "\""
            elif isinstance(self.command, basestring) :
                internal_command.append(str("/usr/bin/sudo -E -S -s '" + str(self.command.decode('utf-8')) + "'"))
                #log_message("Trying to execute: \"" + str(internal_command) + "\"", \
                #            "verbose", message_level)
                #print "Trying to execute: \"" + str(internal_command) + "\""
            try:
                (master, slave) = pty.openpty()
            except Exception, err:
                logMessage("Error trying to open pty: " + str(err))
                raise err
            else:
                try:
                    proc = Popen(internal_command, stdin=slave, stdout=slave, stderr=slave, close_fds=True)
                except Exception, err:
                    logMessage("Error opening process to pty: " + str(err))
                    raise err
                else:
                    #####
                    # Catch the su password prompt
                    # prompt = os.read(master, 512)
                    self.waitnoecho(master, 3)
                    prompt = os.read(master, 512)

                    #####
                    # pass in the password
                    os.write(master, password.strip() + "\n")

                    #####
                    # catch the password
                    prompt = os.read(master, 512)

                    #####
                    # Wait for the next password prompt
                    self.waitnoecho(master, 3)

                    #####
                    # catch the password prompt
                    prompt = os.read(master, 512)

                    #####
                    # Enter the sudo password
                    os.write(master, password + "\n")

                    #####
                    # Catch the password
                    os.read(master, 512)

                    #output = tmp + output
                    while True :
                        r,w,e = select.select([master], [], [], 0) # timeout of 0 means "poll"
                        if r :
                            line = os.read(master, 512)
                            #####
                            # Warning, uncomment at your own risk - several programs
                            # print empty lines that will cause this to break and
                            # the output will be all goofed up.
                            #if not line :
                            #    break
                            #print output.rstrip()
                            output = output + line
                        elif proc.poll() is not None :
                            break
                        #print output.strip()
                    os.close(master)
                    os.close(slave)
                    proc.wait()
                    self.stdout = proc.stdout
                    self.stderr = proc.stderr
                    self.returncode = proc.returncode
                    #print output.strip()
            #output = output.strip()
            #####
            # UNCOMMENT ONLY WHEN IN DEVELOPMENT AND DEBUGGING OR YOU MAY REVEAL
            # MORE THAN YOU WANT TO IN THE LOGS!!!
            #log_message("\n\nLeaving runAs with Sudo: \"" + str(output) + "\"\n\n", "debug", message_level)
            #print "\n\nLeaving runAs with Sudo: \"" + str(output) + "\"\n\n"
            return output

##############################################################################

class RunThread(threading.Thread) :
    """
    Use a thread & subprocess.Popen to run something

    To use - where command could be an array, or a string... :

    run_thread = RunThread(<command>, message_level)
    run_thread.start()
    run_thread.join()
    print run_thread.stdout

    @author: Roy Nielsen
    """
    def __init__(self, command=[], message_level="normal") :
        """
        Initialization method
        """
        self.command = command
        self.message_level = message_level
        self.retout = None
        self.reterr = None
        threading.Thread.__init__(self)

        if isinstance(self.command, types.ListType) :
            self.shell = True
            self.printcmd = " ".join(self.command)
        if isinstance(self.command, types.StringTypes) :
            self.shell = False
            self.printcmd = self.command

        logMessage("Initialized runThread...", "normal", self.message_level)

    ##########################################################################

    def run(self):
        if self.command :
            try :
                p = Popen(self.command, stdout=PIPE,
                                        stderr=PIPE,
                                        shell=self.shell)
            except Exception, err :
                logMessage("Exception trying to open: " + str(self.printcmd), \
                           "normal", self.message_level)
                logMessage("Associated exception: " + str(err), "normal", \
                           self.message_level)
                raise err
            else :
                try:
                    self.retout, self.reterr = p.communicate()
                except Exception, err :
                    logMessage("Exception trying to open: " + \
                               str(self.printcmd), "normal", \
                               self.message_level)
                    logMessage("Associated exception: " + str(err), "normal", \
                               self.message_level)
                    raise err
                else :
                    #logMessage("Return values: ", "debug", self.message_level)
                    #logMessage("retout: " + str(self.retout), "debug", self.message_level)
                    #logMessage("reterr: " + str(self.reterr), "debug", self.message_level)
                    logMessage("Finished \"run\" of: " + str(self.printcmd), \
                               "normal", self.message_level)

    ##########################################################################

    def getStdout(self) :
        """
        Getter for standard output

        @author: Roy Nielsen
        """
        logMessage("Getting stdout...", "verbose", self.message_level)
        return self.retout

    ##########################################################################

    def getStderr(self) :
        """
        Getter for standard err

        @author: Roy Nielsen
        """
        logMessage("Getting stderr...", "verbose", self.message_level)
        return self.reterr

    ##########################################################################

def runMyThreadCommand(cmd=[], message_level="normal") :
    """
    Use the RunThread class to get the stdout and stderr of a command

    @author: Roy Nielsen
    """
    retval = None
    reterr = None

    if cmd and message_level :
        run_thread = RunThread(cmd, message_level)
        run_thread.start()
        run_thread.join()
        retval = run_thread.getStdout()
        reterr = run_thread.getStderr()
    else :
        logMessage("Invalid parameters, please report this as a bug.")

    return retval, reterr

