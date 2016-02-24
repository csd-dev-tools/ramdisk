"""
Helper functions, OS agnostic

@author: Roy Nielsen
"""

from subprocess import Popen, STDOUT, PIPE

def getOsFamily():
    """
    Get the os name from the "uname -s" command

    @author: Roy Nielsen
    """
    cmd = ["/usr/bin/uname", "-s"]

    output = Popen(cmd, stdout=PIPE, stderr=STDOUT).communicate()[0]

    operatingsystem = output.strip().lower()

    return operatingsystem

