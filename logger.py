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
import time
import calendar
import datetime
import logging

def IllegalExtensionTypeError(Exception):
    """
    Custom Exception
    """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

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

@singleton
class Logger(object):
    """
    """
    def __init__(self, level="DEBUG"):
        """
        """
        if self.validateLevel(level):
            self.lvl = level
        self.filename = ""
        self.levels = {"NOTSET" : 0, "DEBUG" : 10, "INFO" : 20, "WARNING" : 30,
                       "ERROR" : 40, "CRITICAL" : 50}
        self.logHanlder = None
        self.logHandlers = []

    #############################################

    def setLoggingLevel(self, level=""):
        """
        """
        success = False
        if self.validateLevel():
            self.lvl = level
            success = True
        return success

    #############################################

    def validateLevel(self, level="NOTSET"):
        success = False
        if level in self.levels:
            self.lvl = level
            success = True
        return success

    #############################################

    def setUpStandardHanlders(self,  filename = "",
                                     extension_type="inc",
                                     log_count=10,
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
                self.filename = filename + "." + calendar.timegm(time.gmtime())
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

    def go(self, lvl=0, msg=""):
        """
        """
        if int(lvl) > 0 and int(lvl) <= 50:
             
