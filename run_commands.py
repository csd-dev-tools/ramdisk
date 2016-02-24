"""
Library for running executables from the command line in different ways

@author: Roy Nielsen
"""
import re
import types
import threading
from subprocess import Popen, PIPE

from log_message import logMessage

##############################################################################

def systemCallRetVal(cmd="", message_level="normal", myshell=False) :
    """
    Use the subprocess module to execute a command, returning
    the output of the command

    @author: Roy Nielsen
    """
    retval = ""
    reterr = ""

    if isinstance(cmd, types.ListType) :
        printcmd = " ".join(cmd)
    if isinstance(cmd, types.StringTypes) :
        printcmd = cmd

    try :
        if not myshell :
            pipe = Popen(cmd, stdout=PIPE, stderr=PIPE)
        elif myshell :
            pipe = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=myshell)
        else :
            pipe = Popen(cmd, stdout=PIPE, stderr=PIPE)

        (stdout_out, stderr_out) = pipe.communicate()

        if stdout_out :
            for line in stdout_out :
                if line is not None :
                    line.strip("\n")
                    retval = retval + line

        if stderr_out :
            for line in stderr_out :
                if line is not None :
                    line.strip("\n")
                    reterr = reterr + line

    except ValueError, err :
        logMessage("system_call_retval - ValueError: " + \
                   str(err) + " command: " + printcmd, "normal", \
                   message_level)
    except OSError, err :
        logMessage("system_call_retval - OSError: " + str(err) + \
                   " command: " + printcmd, "normal", message_level)
    except IOError, err :
        logMessage("system_call_retval - IOError: " + str(err) + \
                   " command: " + printcmd, "normal", message_level)
    except Exception, err :
        logMessage("system_call_retval - Unexpected Exception: "  + \
                   str(err)  + " command: " + printcmd, "normal", \
                   message_level)
    else :
        logMessage(printcmd + \
                    " Returned with error/returncode: " + \
                    str(pipe.returncode), \
                    "debug", \
                    message_level)
        pipe.stdout.close()
    finally:
        logMessage("Done with command: " + printcmd, \
                    "verbose", \
                    message_level)
    return (retval, reterr)

##############################################################################

def runWithWaitTillFinished(command=[], message_level="normal") :
    """
    Use subprocess to call a command and wait until it is finished before
    moving on...

    @author: Roy Nielsen
    """
    if command :
        if isinstance(command, types.ListType) :
            printcmd = " ".join(command)
        if isinstance(command, types.StringTypes) :
            printcmd = command
        proc = Popen(command, stdout=PIPE, stderr=PIPE)
        proc.wait()
        logMessage("command: " + printcmd + " returned: " + \
                   str(proc.returncode), "verbose", message_level)
        return proc.returncode
    else :
        logMessage("Cannot run a command that is empty...", "normal", message_level)

##############################################################################

def kill_proc(proc, timeout) :
    """
    Support function for the "runWithTimeout" function below

    @author: Roy Nielsen
    """
    timeout["value"] = True
    proc.kill()

##############################################################################

def runWithTimeout(command, timout_sec, message_level="normal") :
    """
    Run a command with a timeout - return:
    Returncode of the process
    stdout of the process
    stderr of the process
    timout - True if the command timed out
             False if the command completed successfully

    @author: Roy Nielsen
    """
    if isinstance(command, list) :
        if not command :
            logMessage("Cannot run a command with a command list that is " + \
                       "empty...", "normal", message_level)
            return False, False, False, False
    elif isinstance(command, basestring) :
        if re.match("^\s+$", command) or re.match("^$", command) :
            logMessage("Cannot run a command with a command that is an " + \
                       "empty string...", "normal", message_level)
            return False, False, False, False

    proc = Popen(command, stdout=PIPE, stderr=PIPE)

    timeout = {"value" : False}
    timer = threading.Timer(timout_sec, kill_proc, [proc, timeout])
    timer.start()
    stdout, stderr = proc.communicate()
    timer.cancel()

    return proc.returncode, stdout, stderr, timeout["value"]

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

