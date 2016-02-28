"""
Helper functions, OS agnostic

@author: Roy Nielsen
"""
import sys
from subprocess import Popen, STDOUT, PIPE

def getOsFamily():
    """
    Get the os name from the "uname -s" command

    @author: Roy Nielsen
    """

    operatingsystemfamily = sys.platform

    return operatingsystemfamily

