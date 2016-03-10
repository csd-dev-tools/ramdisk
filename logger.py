"""
A module for logging to different facilities...

Python logging references:
https://docs.python.org/2/library/logging.html
https://docs.python.org/2/library/logging.handlers.html
https://docs.python.org/2/library/logging.config.html
https://docs.python.org/2/howto/logging.html
https://docs.python.org/2/howto/logging-cookbook.html
https://docs.python.org/2/library/hotshot.html
https://docs.python.org/2/library/multiprocessing.html?highlight=logging#logging

@author: Roy Nielsen
"""
import re
import time
import socket
import calendar
import datetime
import logging

###############################################################################
# Exception setup

def IllegalExtensionTypeError(Exception):
    """
    Custom Exception
    """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

def IllegalLoggingLevelError(Exception):
    """
    Custom Exception
    """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

###############################################################################
# Setting up a funciton for a singleton

def singleton(cls):
    """
    Adapted from: https://www.python.org/dev/peps/pep-0318/ Example #2
    """
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

###############################################################################
# Main class

@singleton
class Logger(object):
    """
    """
    def __init__(self, environment=None, debug_mode=False, verbose_mode=False, level=-1):
        """
        """
        self.lvl = level
        if environment:
            self.environment = environment
            if re.match("^debug$", self.environment.getdebugmode()):
                self.lvl = 10
            elif re.match("^verbose$", self.environment.getdebugmode()):
                self.lvl = 20
        elif debug_mode or verbose_mode:
            if debug_mode:
                self.lvl = 10
            elif verbose_mode:
                self.lvl = 20
        else:
            if not int(self.lvl) > 0:
                self.lvl = 10
            elif self.validateLevel(level):
                self.lvl = level
        self.filename = ""
        self.levels = {"NOTSET" : 0, "DEBUG" : 10, "INFO" : 20, "WARNING" : 30,
                       "ERROR" : 40, "CRITICAL" : 50}
        self.logr = None
        self.logrs = {"root" : ""}

    #############################################

    def setInitialLoggingLevel(self, level=""):
        """
        """
        success = False
        if self.validateLevel():
            self.lvl = level
            success = True
        return success

    #############################################

    def validateLevel(self, level=-1):
        success = False
        if int(level) > 0 and int(level) <= 60:
            self.lvl = level
            success = True
        else:
            raise IllegalLoggingLevelError("Not a valid value for a logging level.")
        return success

    #############################################

    def initializeLogs(self,  filename = "",
                       extension_type="inc",
                       logCount=10,
                       size=10000000,
                       syslog=False,
                       myconsole=True):
        """
        Sets up some basic logging.  For more configurable logging, use the
        setUpLogger & setUpHandler methods.

        @param: filename: Name of the file you would like to log to. String

        @param: extension_type: type of extension to use on the filename. String
                  none:  overwrite the file currently with the passed in name
                 epoch:  time since epoch
                  time:  date/time stamp .ccyymmdd.hhmm.ss in military time
                   inc:  will increment log number similar to logrotate.

        @param: log_count:  if "inc" is used above, the count of logs to keep
                            Default keep the last 10 logs.  Int

        @param: size   :  if "inc", the size to allow logs to get. Default 10Mb. Int

        @param: syslog : Whether or not to log to syslog. Bool

        @param: console: Whether or not to log to the console. Bool

        @NOTE: This only sets up the root logger.

        @note: Interface borrowed from Stonix's LogDispatcher.initializeLogs
               authored by scmcleni, D. Kennel and R. Nielsen

        @author: Roy Nielsen
        """
        success = False
        rotate = False
        if extension_type in ["none", "epoch", "time", "inc", "sys"]:
            if extension_type == "none":
                ####
                # No file extension, just use the filename...
                self.filename = filename
            if extension_type == "epoch":
                ####
                # Use a file extension using the time library "since epoch"
                self.filename = filename + "." + str(time.time())
            if extension_type == "time":
                ####
                # Use a file extension using the datetime library
                # Get the UTC time and format a time stamp string
                # using format YYYYMMDD.HHMMSS.microseconds
                datestamp = datetime.datetime.utcnow()
                stamp = datestamp.strftime("%Y%m%d.%H%M%S.%f")
                self.filename = filename + "." + str(stamp)
            if extension_type == "inc":
                #####
                # Get a log rotation method set up.
                rotate = True
                self.filename = filename
        else:
            raise IllegalExtensionTypeError("Cannot use this " + \
                                            "configuration: " + \
                                            str(extension_type))
        #####
        # Initialize the root logger
        self.logr = logging.getLogger("")

        #####
        # Set logging level for the root logger
        if not rotate:
            #####
            # Set up a regular root log handler
            fileHandler = logging.FileHandler(self.filename)
            formatter = self.formatLoggingString()
            fileHandler.setFormatter(formatter)
        else:
            #####
            # Set up the RotatingFileHandler
            rotHandler = logging.handlers.RotatingFileHandler(self.filename,
                                                              maxBytes=size,
                                                              backupCount=logCount)
            formatter = self.formatLoggingString()
            rotHandler.setFormatter(formatter)

        if myconsole:
            #####
            # Set up StreamHandler to log to the console
            conHandler = logging.StreamHandler()
            formatter = self.formatLoggingString()
            conHandler.setFormatter(formatter)
        if syslog:
            #####
            # Set up the SysLogHandler
            sysHandler = logging.handlers.SysLogHandler()
            formatter = self.formatLoggingString()
            sysHandler.setFormatter(formatter)

        #####
        # Add applicable handlers to the logger
        if not rotate:
            self.logr.addHandler(fileHandler)
        elif rotate:
            self.logr.addHandler(rotHandler)

        if myconsole:
            self.logr.addHandler(conHandler)
        if syslog:
            try:
                self.logr.addHandler(sysHandler)
            except socket.error:
                self.log(40, "Syslog not accepting connections!")

        #####
        # Set the log level
        self.logr.setLevel(self.lvl)

    #############################################

    def setUpHandler(self, *args, **kwargs):
        """
        Template/interface for children to use for setting up specific handlers.

        In future there should be children, or methods to handle different
        log handlers...

        @author: Roy Nielsen
        """
        pass

    #############################################

    def setUpLogger(self, *args, **kwargs):
        """
        Template/interface for setting up a logger

        One may add several handlers to one logger.

        @author: Roy Nielsen
        """
        pass

    #############################################

    def formatLoggingString(self):
        """
        Will set the logging level of the current self.logr.

        @author: Roy Nielsen
        """
        #####
        # Process via logging level
        if int(self.lvl) > 0 and int(self.lvl) < 10:
            # Quiet, no logging, no formatting...
            formatter = logging.Formatter('')
        elif int(self.lvl) >= 10 and int(self.lvl) < 20:
            #####
            # Debug
            formatter = logging.Formatter('%(asctime)s %(name)S %(levelname)s'+\
                                          ' %(module)s %(funcName)s %(lineno)s'+\
                                          ' %(message)s')
        elif int(self.lvl) >= 20 and int(self.lvl) < 30:
            #####
            # Info
            formatter = logging.Formatter('%(asctime)s %(levelname)s ' + \
                                          '%(module)s %(lineno)s %(message)s')
        elif int(self.lvl) >=30 and int(self.lvl) < 40:
            #####
            # Warning
            formatter = logging.Formatter('%(asctime)s %(levelname)s ' + \
                                          '%(module)s %(lineno)s %(message)s')
        elif int(self.lvl) >= 40 and int(self.lvl) < 50:
            #####
            # Error
            formatter = logging.Formatter('%(asctime)s %(levelname)s ' + \
                                          '%(module)s %(lineno)s %(message)s')
        elif int(self.lvl) >= 50 and int(self.lvl) < 60:
            #####
            # Critical
            formatter = logging.Formatter('%(asctime)s %(levelname)s ' + \
                                          '%(module)s %(lineno)s %(message)s')
        else:
            formatter = logging.Formatter('')
            raise IllegalLoggingLevelError("Not a valid value for a logging level.")

        return formatter

    #############################################

    def log(self, priority=0, msg=""):
        """
        Interface to work similar to Stonix's LogDispatcher.log

        @note: Stonix's LogDispatcher.log authored by: scmcleni

        @author: Roy Nielsen
        """
        pri = str(priority)
        if re.match("^\d\d$", pri):
            #####
            # Process via numerical logging level
            self.logr.log(int(priority), msg)
        else:
            raise IllegalLoggingLevelError("Not a valid value for a logging level.")

###############################################################################
# Helper class

class LogPriority(object):
    """
    Similar to LogPriority in the Stonix project LogDispatcher, only using
    numbers instead of strings.

    @note: Author of the Stonix LogPriority is scmcleni
    """
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
