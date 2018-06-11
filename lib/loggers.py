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
from __future__ import absolute_import
import os
import re
import sys
import time
import socket
import inspect
import datetime
import traceback
import logging
import logging.handlers
#from logging.handlers import RotatingFileHandler
#sys.path.append("..")
###############################################################################
# Exception setup

class IllegalExtensionTypeError(Exception):
    """
    Custom Exception
    """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class IllegalLoggingLevelError(Exception):
    """
    Custom Exception
    """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class EnvironmentError(Exception):
    """
    Custom Exception
    """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

###############################################################################
# Setting up a function for a singleton

def singleton_decorator(cls):
    """
    Adapted from: https://www.python.org/dev/peps/pep-0318/ Example #2 and:
    """
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


class SingletonCyLogger(type):
    """
    This class was retrieved from: http://stackoverflow.com/questions/33364070/python-implementing-singleton-as-metaclass-but-for-abstract-classes
    Modified class origionally authored by: Martijn Pieters(http://stackoverflow.com/users/100297/martijn-pieters)
    with license: https://creativecommons.org/licenses/by-sa/3.0/
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonCyLogger, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


###############################################################################
# Main class

class CyLogger(object):
    __metaclass__ = SingletonCyLogger
    """
    Class to set up logging, with easy string referencing loggers and their
    handlers.
    
    @author: Roy Nielsen
    """
    
    instanciatedLoggers = {}

    def __init__(self, environ=False, debug_mode=False, verbose_mode=False, level=30):
        """
        """
        # print ".............Level: " + str(level)
        self.lvl = int(level)
        '''
        if environ:
            self.environment = environ
            try:
                envDebugMode = self.environment.getdebugmode()
                envVerboseMode = self.environment.getverbosemode()
            except IndexError:
                pass
            if re.match("^debug$", envDebugMode):
                self.lvl = 10
            elif re.match("^verbose$", envVerboseMode):
                self.lvl = 20
        '''
        if debug_mode or verbose_mode:
            if debug_mode:
                self.lvl = 10
            elif verbose_mode:
                self.lvl = 20
        #####
        # If the first three aren't passed in, make a guess based on level
        if self.lvl < 0:
            self.lvl = 20
        elif self.lvl > 0:
            self.validateLevel(self.lvl)
        else:
            self.lvl = 30

        self.filename = ""
        self.syslog = False
        self.logr = None
        self.logrs = {"root" : ""}

    #############################################

    def setInitialLoggingLevel(self, level=30):
        """
        """
        success = False
        if self.validateLevel():
            self.lvl = level
            success = True
        return success

    #############################################

    def validateLevel(self, level=30):
        """
        Input validation for the logging level

        @author: Roy Nielsen
        """
        
        success = False
        if int(level) > 0 and int(level) <= 60:
            self.lvl = level
            success = True
        else:
            raise IllegalLoggingLevelError("Not a valid value for a logging level.")
        return success

    #############################################

    def doRollover(self, rothandler):
        """
        If there is a RotatingFileHandler attached to the active logger,
        rotate the log.
        
        @author: Roy Nielsen
        """
        if self.rotate:
            try:
                self.logr.handlers.RotatingFileHandler.doRollover()
            except Exception, err:
                self.logr.log(LogPriority.WARNING, "Exception: " + str(err))

    #############################################

    def initializeLogs(self,  logdir = "/tmp", 
                       filename = "",
                       extension_type="inc",
                       logCount=10,
                       size=10000000,
                       syslog=True,
                       myconsole=True):
        """
        Sets up some basic logging.  For more configurable logging, use the
        setUpLogger & setUpHandler methods.

        @param: logdir: Directory to place the logs

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
        if not filename:
            filename = sys.argv[0].split("/")[-1]
        success = False
        self.syslog = syslog
        self.rotate = False
        self.fileHandler = False
        if extension_type in ["none", "epoch", "time", "inc", "sys"]:
            if extension_type == "none":
                ####
                # No file extension, just use the filename...
                self.filename = filename + ".log"
            if extension_type == "epoch":
                ####
                # Use a file extension using the time library "since epoch"
                self.filename = filename + "." + str(time.time()) + ".log"
            if extension_type == "time":
                ####
                # Use a file extension using the datetime library
                # Get the UTC time and format a time stamp string
                # using format YYYYMMDD.HHMMSS.microseconds
                # 2016/03/11 - Changing to use .now instead of .utcnow
                # to the time stamp can be correlated with system logs...
                datestamp = datetime.datetime.now()
                stamp = datestamp.strftime("%Y%m%d.%H%M%S.%f")
                self.filename = filename + "." + str(stamp) + ".log"
            if extension_type == "inc":
                #####
                # Get a log rotation method set up.
                self.rotate = True
                self.filename = filename + ".log"
        else:
            raise IllegalExtensionTypeError("Cannot use this " + \
                                            "configuration: " + \
                                            str(extension_type))
        #####
        # Concatinate the logdir with the self.filename to give the
        # self.filename the intended full path
        self.filename = os.path.join(logdir, self.filename)

        #####
        # Initialize the root logger
        self.logr = logging.getLogger("")

        #####
        # Set logging level for the root logger
        if not self.rotate:
            #####
            # Set up a regular root log handler
            fileHandler = logging.FileHandler(self.filename)
            self.fileHandler = True
        else:
            #####
            # Set up the RotatingFileHandler
            rotHandler = logging.handlers.RotatingFileHandler(self.filename,
                                                              maxBytes=size,
                                                              backupCount=logCount)
        if myconsole:
            #####
            # Set up StreamHandler to log to the console
            conHandler = logging.StreamHandler()
        if self.syslog:
            #####
            # Set up the SysLogHandler
            try:
                sysHandler = logging.handlers.SysLogHandler()
            except socket.error:
                print("Socket error, can't connect to syslog...")
                self.syslog = False

        #####
        # Add applicable handlers to the logger
        if not self.rotate and self.fileHandler:
            self.logr.addHandler(fileHandler)
            self.logr.log(LogPriority.DEBUG,"Added FileHandler")
        elif self.rotate:
            self.logr.addHandler(rotHandler)
            self.logr.log(LogPriority.DEBUG,"Added RotatingFileHandler")
            #self.doRollover(rotHandler)

        if myconsole:
            self.logr.addHandler(conHandler)
            self.logr.log(LogPriority.DEBUG,"Added StreamHandler")
        if self.syslog:
            try:
                self.logr.addHandler(sysHandler)
                self.logr.log(LogPriority.DEBUG,"Added SyslogHanlder")
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

    def log(self, priority, msg):
        """
        Interface to work similar to Stonix's LogDispatcher.py

        @note: Stonix's LogDispatcher.py authored by: scmcleni

        @author: Roy Nielsen
        """
        pri = str(priority)
        if re.match("^\d\d$", pri) and self.validateLevel():
            validatedLvl = int(pri)
        else:
            raise IllegalLoggingLevelError("Cannot log at this priority level: " + pri)
        
        if not msg:
            return
        
        ####
        # Use the datetime library to get the time for a timestamp
        # using format YYYYi-MM-DD-HH-MM-SS
        # Only dash separators are used to make for easy numeric processing
        # using local time so the time stamp can be correlated with 
        # system logs...
        datestamp = datetime.datetime.now()
        timestamp = datestamp.strftime("%Y-%m-%d-%H-%M-%S")

        #####
        # Get the name of the program using this library
        prog = sys.argv[0].split("/")[-1]

        #####
        # Get the filename of the code calling CrazyLogger.log()
        # members = inspect.getmembers(inspect.stack(), inspect.iscode)
        # print "Members: " + str(members)
        # co_filename = members[1][3]

        (frame, fullLengthFilename, line_number, function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
        filename = fullLengthFilename.split("/")[-1]

        if not self.syslog:
            #####
            # longPrefix message to be in the format: 
            # <timestamp> <calling_script_name> : <filename_of_calling_function>, <name_of_calling_function> (<line number of calling function>)
            longPrefix = '{} {} : {}, {} ({}) '.format(str(timestamp),
                                                       str(prog), 
                                                       str(filename), 
                                                       str(function_name), 
                                                       str(line_number))
            #####
            # shorterFormat message to be in the format: 
            # <timestamp> <calling_script_name> : <name_of_calling_function> (<line number of calling function>)
            shortFormat = '{} {} : {} ({}) '.format(str(timestamp),
                                                    str(prog),
                                                    str(function_name),
                                                    str(line_number))
        else:
            #####
            # longPrefix message to be in the format: 
            # <calling_script_name> : <filename_of_calling_function>, <name_of_calling_function> (<line number of calling function>)
            longPrefix = '{} : {}, {} ({}) '.format(str(prog), 
                                                    str(filename), 
                                                    str(function_name), 
                                                    str(line_number))
            #####
            # shorterFormat message to be in the format: 
            # <calling_script_name> : <name_of_calling_function> (<line number of calling function>)
            shortFormat = '{} : {} ({}) '.format(str(prog),
                                                 str(function_name), 
                                                 str(line_number))
        msg_list = []
        if not msg:
            return
        if isinstance(msg, basestring) and "\n" not in msg:
            msg_list = [msg]
        elif isinstance(msg, basestring) and "\n" in msg:
            first_msg_list = msg.split("\n")
            for mymsg in first_msg_list:
                msg_list.append(mymsg + "\n")
        elif msg and isinstance(msg, list):
            msg_list = msg
        elif isinstance(msg, dict):
            for key, value in msg.iteritems():
                msg_list.append(str(key) + " : " + str(value))
        else:
            msg_list = [str(msg)]

        for line in msg_list:
            #####
            # Process via logging level
            if int(self.lvl) > 0 and int(self.lvl) < 10:
                # Quiet, no prefix or formatting...
                self.logr.log(validatedLvl, str(line))
    
            elif int(self.lvl) >= 10 and int(self.lvl) < 20:
                #####
                # Debug
                self.logr.log(validatedLvl, longPrefix + "DEBUG: (" + pri + ") " + str(line))
            elif int(self.lvl) >= 20 and int(self.lvl) < 30:
                #####
                # Info
                self.logr.log(validatedLvl, longPrefix + "DEBUG: (" + pri + ") " + str(line))
            elif int(self.lvl) >=30 and int(self.lvl) < 40:
                #####
                # Warning
                try:
                    self.logr.log(validatedLvl, longPrefix + "DEBUG: (" + str(pri) + ") " + str(line))
                except Exception, err:
                    self.logr.log(LogPriority.DEBUG, str(traceback.format_exc()))
                    self.logr.log(LogPriority.DEBUG, str(err))
            elif int(self.lvl) >= 40 and int(self.lvl) < 50:
                #####
                # Error
                self.logr.log(validatedLvl, longPrefix + "DEBUG: (" + pri + ") " + str(line))
            elif int(self.lvl) >= 50 and int(self.lvl) < 60:
                #####
                # Critical
                self.logr.log(validatedLvl, longPrefix + "DEBUG: (" + pri + ") " + str(line))
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
    DEBUG = int(10)
    INFO = int(20)
    VERBOSE = int(20)
    WARNING = int(30)
    ERROR = int(40)
    CRITICAL = int(50)

