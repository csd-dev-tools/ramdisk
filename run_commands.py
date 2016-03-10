"""
Library for running executables from the command line in different ways

Inspiration for some of the below found on the internet.

@author: Roy Nielsen
"""
import os
import re
import pty
import sys
import time
import types
import select
import termios
import threading
from subprocess import Popen, PIPE

from logger import Logger
from logger import LogPriority as lp

def OSNotValidForRunWith(Exception):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

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

    @WARNING - Known to work on Mac, may or may not work on other platforms

    @author: Roy Nielsen
    """
    def __init__(self, logger):
        self.command = None
        self.output = None
        self.error = None
        self.module_version = '20160224.184019.673753'
        self.returncode = None
        self.printcmd = None
        self.myshell = None
        self.logger = logger

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

    ############################################################################

    def getStdout(self):
        """
        Getter for the standard output of the last command.

        @author: Roy Nielsen
        """
        return self.output

    ############################################################################

    def getStderr(self):
        """
        Getter for the standard error of the last command.

        @author: Roy Nielsen
        """
        return self.error

    ############################################################################

    def getReturnCode(self):
        """
        Getter for the return code of the last command.

        @author: Roy Nielsen
        """
        return self.returncode

    ############################################################################

    def getNlogReturns(self):
        """
        Getter for the retval, reterr & retcode of the last command.

        Will also log the values

        @author: Roy Nielsen
        """
        self.logger(lp.INFO, "Output: " + str(self.output))
        self.logger(lp.INFO, "Error: " + str(self.error))
        self.logger(lp.INFO, "Return code: " + str(self.returncode))
        return self.output, self.error, self.returncode

    ############################################################################

    def getNprintReturns(self):
        """
        Getter for the retval, reterr & retcode of the last command.

        Will also print the values

        @author: Roy Nielsen
        """
        print "Output: " + str(self.output)
        print "Error: " + str(self.error)
        print "Return code: " + str(self.returncode)
        return self.output, self.error, self.returncode

    ############################################################################

    def communicate(self) :
        """
        Use the subprocess module to execute a command, returning
        the output of the command

        @author: Roy Nielsen
        """
        if self.command:
            try :
                proc = Popen(self.command,
                             stdout=PIPE, stderr=PIPE, shell=self.myshell)

                self.output, self.error = proc.communicate()

            except Exception, err :
                self.logger(lp.WARNING, "system_call_retval - Unexpected Exception: "  + \
                           str(err)  + " command: " + self.printcmd)
                raise err
            else :
                self.logger(lp.DEBUG, self.printcmd + \
                            " Returned with error/returncode: " + \
                            str(proc.returncode))
                proc.stdout.close()
            finally:
                self.logger(lp.DEBUG, "Done with command: " + self.printcmd)
                self.returncode = proc.returncode
        else :
            self.logger(lp.WARNING, "Cannot run a command that is empty...")
            self.output = None
            self.error = None
            self.returncode = None

    ############################################################################

    def wait(self) :
        """
        Use subprocess to call a command and wait until it is finished before
        moving on...

        @author: Roy Nielsen
        """
        if self.command :
            try:
                proc = Popen(self.command,
                             stdout=PIPE, stderr=PIPE, shell=self.myshell)
                proc.wait()
                for line in proc.stdout.readline():
                    self.output = self.output + line
                for line in proc.stderr.readline():
                    self.error = self.error + line
            except Exception, err:
                self.logger(lp.WARNING, "system_call_retval - Unexpected Exception: "  + \
                           str(err)  + " command: " + self.printcmd)
                raise err
            else :
                self.logger(lp.DEBUG, self.printcmd + \
                            " Returned with error/returncode: " + \
                            str(proc.returncode))
                proc.stdout.close()
            finally:
                self.logger(lp.DEBUG, "Done with command: " + self.printcmd)
                self.stdout = proc.stdout
                self.stderr = proc.stderr
                self.returncode = proc.returncode
        else :
            self.logger(lp.WARNING, "Cannot run a command that is empty...")
            self.stdout = None
            self.stderr = None
            self.returncode = None

    ############################################################################

    def killProc(self, proc, timeout) :
        """
        Support function for the "runWithTimeout" function below

        @author: Roy Nielsen
        """
        timeout["value"] = True
        proc.kill()

    ############################################################################

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
                proc = Popen(self.command,
                             stdout=PIPE, stderr=PIPE, shell=self.myshell)

                timeout = {"value" : False}
                timer = threading.Timer(timout_sec, self.killProc,
                                        [proc, timeout])
                timer.start()
                self.output, self.error = proc.communicate()
                timer.cancel()
                self.returncode = proc.returncode
            except Exception, err:
                self.logger(lp.WARNING, "system_call_retval - Unexpected " + \
                            "Exception: "  + str(err)  + \
                            " command: " + self.printcmd)
                raise err
            else :
                self.logger(lp.DEBUG, self.printcmd + \
                            " Returned with error/returncode: " + \
                            str(proc.returncode))
                proc.stdout.close()
            finally:
                self.logger(lp.DEBUG, "Done with command: " + self.printcmd)
        else :
            self.logger(lp.WARNING, "Cannot run a command that is empty...")
            self.stdout = None
            self.stderr = None
            self.returncode = None

        return timeout["value"]

    ############################################################################

    def runAs(self, user="", password="") :
        """
        Use pexpect to run "su" to run a command as another user...

        Required parameters: user, password, command

        @author: Roy Nielsen
        """
        if re.match("^\s*$", user) or \
           re.match("^\s*$", password) or \
           not self.command :
            self.logger(lp.WARNING, "Cannot pass in empty parameters...")
            self.logger(lp.WARNING, "user = \"" + str(user) + "\"")
            self.logger(lp.WARNING, "check password...")
            self.logger(lp.WARNING, "command = \"" + str(self.command) + "\"")
            return(255)
        else :
            output = ""
            internal_command = ["/usr/bin/su", "-", str(user), "-c"]

            if isinstance(self.command, list) :
                internal_command.append(" ".join(self.command))
                #log_message("Trying to execute: \"" + \
                #            " ".join(internal_command) + "\"", \
                #            "verbose", message_level)
            elif isinstance(self.command, basestring) :
                internal_command.append(self.command)
                #log_message("Trying to execute: \"" + \
                #            str(internal_command) + "\"", \
                #            "verbose", message_level)

            (master, slave) = pty.openpty()

            proc = Popen(internal_command,
                         stdin=slave, stdout=slave, stderr=slave,
                         close_fds=True)

            prompt = os.read(master, 10)

            if re.match("^Password:", str(prompt)) :
                os.write(master, password + "\n")
                line = os.read(master, 512)
                output = output + line
                while True :
                    #####
                    # timeout of 0 means "poll"
                    r,w,e = select.select([master], [], [], 0) 
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
            #log_message("Leaving runAs with: \"" + str(output) + "\"",
            #            "debug", message_level)
            return output

    ############################################################################

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

    ############################################################################

    def waitnoecho (self, fileDescriptor, timeout=3):
        """This waits until the terminal ECHO flag is set False. This returns
        True if the echo mode is off. This returns False if the ECHO flag was
        not set False before the timeout. This can be used to detect when the
        child is waiting for a password. Usually a child application will turn
        off echo mode when it is waiting for the user to enter a password. For
        example, instead of expecting the "password:" prompt you can wait for
        the child to set ECHO off::

            see below in runAsWithSudo

        If timeout is None or negative, then this method to block forever until
        ECHO flag is False.

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

    ############################################################################

    def runAsWithSudo(self, user="", password="") :
        """
        Use pty method to run "su" to run a command as another user...

        Required parameters: user, password, command

        @author: Roy Nielsen
        """
        self.logger(lp.DEBUG, "Starting runAsWithSudo: ")
        self.logger(lp.DEBUG, "\tuser: \"" + str(user) + "\"")
        self.logger(lp.DEBUG, "\tcmd : \"" + str(self.command) + "\"")
        if re.match("^\s+$", user) or re.match("^\s+$", password) or \
           not user or not password or \
           not self.command :
            self.logger(lp.WARNING, "Cannot pass in empty parameters...")
            self.logger(lp.WARNING, "user = \"" + str(user) + "\"")
            self.logger(lp.WARNING, "check password...")
            self.logger(lp.WARNING, "command = \"" + str(self.command) + "\"")
            return(255)
        else :
            output = ""

            internal_command = ["/usr/bin/su", str("-"),
                                str(user).strip(), str("-c")]

            if isinstance(self.command, list) :
                cmd = []
                for i in range(len(self.command)):
                    try:
                        cmd.append(str(self.command[i].decode('utf-8')))
                    except UnicodeDecodeError :
                        cmd.append(str(self.command[i]))

                internal_command.append(str("/usr/bin/sudo -E -S -s '" + \
                                            " ".join(cmd) + "'"))
                #log_message("Trying to execute: \"" + \
                #            " ".join(internal_command) + "\"", \
                #            "verbose", message_level)
                #print "Trying to execute: \"" + " ".join(internal_command) + \
                #       "\""
            elif isinstance(self.command, basestring) :
                internal_command.append(str("/usr/bin/sudo -E -S -s " + \
                                            "'" + \
                                            str(self.command.decode('utf-8'))+ \
                                            "'"))
                #log_message("Trying to execute: \"" + str(internal_command) + \
                #            "\"", "verbose", message_level)
                #print "Trying to execute: \"" + str(internal_command) + "\""
            try:
                (master, slave) = pty.openpty()
            except Exception, err:
                self.logger(lp.WARNING, "Error trying to open pty: " + str(err))
                raise err
            else:
                try:
                    proc = Popen(internal_command,
                                 stdin=slave, stdout=slave, stderr=slave,
                                 close_fds=True)
                except Exception, err:
                    self.logger(lp.WARNING, "Error opening process to pty: " + \
                                str(err))
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
                        #####
                        # timeout of 0 means "poll"
                        r,w,e = select.select([master], [], [], 0)
                        if r :
                            line = os.read(master, 512)
                            #####
                            # Warning, uncomment at your own risk - several
                            # programs print empty lines that will cause this
                            # to break and the output will be all goofed up.
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
            #log_message("\n\nLeaving runAs with Sudo: \"" + str(output) + \
            #            "\"\n\n", "debug", message_level)
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
    def __init__(self, command=[], logger=None) :
        """
        Initialization method
        """
        self.command = command
        self.logger = logger
        self.retout = None
        self.reterr = None
        threading.Thread.__init__(self)

        if isinstance(self.command, types.ListType) :
            self.shell = True
            self.printcmd = " ".join(self.command)
        if isinstance(self.command, types.StringTypes) :
            self.shell = False
            self.printcmd = self.command

        self.logger(lp.INFO, "Initialized runThread...")

    ##########################################################################

    def run(self):
        if self.command :
            try :
                p = Popen(self.command, stdout=PIPE,
                                        stderr=PIPE,
                                        shell=self.shell)
            except Exception, err :
                self.logger(lp.WARNING, "Exception trying to open: " + \
                            str(self.printcmd))
                self.logger(lp.WARNING, "Associated exception: " + str(err))
                raise err
            else :
                try:
                    self.retout, self.reterr = p.communicate()
                except Exception, err :
                    self.logger(lp.WARNING, "Exception trying to open: " + \
                               str(self.printcmd))
                    self.logger(lp.WARNING, "Associated exception: " + str(err))
                    raise err
                else :
                    #logMessage("Return values: ", "debug", self.message_level)
                    #logMessage("retout: " + str(self.retout),
                    #           "debug", self.message_level)
                    #logMessage("reterr: " + str(self.reterr),
                    #           "debug", self.message_level)
                    self.logger(lp.WARNING, "Finished \"run\" of: " + \
                                str(self.printcmd))

    ##########################################################################

    def getStdout(self) :
        """
        Getter for standard output

        @author: Roy Nielsen
        """
        self.logger(lp.INFO, "Getting stdout...")
        return self.retout

    ##########################################################################

    def getStderr(self) :
        """
        Getter for standard err

        @author: Roy Nielsen
        """
        self.logger(lp.DEBUG, "Getting stderr...")
        return self.reterr

##############################################################################

def runMyThreadCommand(cmd=[], logger=None) :
    """
    Use the RunThread class to get the stdout and stderr of a command

    @author: Roy Nielsen
    """
    retval = None
    reterr = None
    if cmd and logger :
        run_thread = RunThread(cmd, logger)
        run_thread.start()
        run_thread.join()
        retval = run_thread.getStdout()
        reterr = run_thread.getStderr()
    else :
        logger(lp.INFO, "Invalid parameters, please report this as a bug.")

    return retval, reterr

