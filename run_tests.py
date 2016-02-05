#!/usr/bin/python
"""
Example of using a "Test Suite" with a directory listing. . .

@author: Roy Nielsen
@note Initial working model: 1/15/2015
"""
import os
import re
import sys
import unittest
sys.path.append("./test")
def suite():
    """
    Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()

    allfiles = os.listdir("./test")
    print str(allfiles)
    for testfile in allfiles:
        if re.match("^test_.*\.py$", str(testfile)):
            test_name = str(testfile).split(".")[0]
            pycfile = os.path.join("./test", test_name + ".pyc")
            if os.path.exists(pycfile):
                os.unlink(pycfile)
            ################################################
            # Test class needs to be named the same as the 
            #   filename for this to work.
            # import the file named in "test_name" variable
            test_to_run = __import__(test_name)
            # getattr(x, 'foobar') is equivalent to x.foobar
            test_to_run = getattr(test_to_run, test_name)
            # Add the test class to the test suite
            test_suite.addTest(unittest.makeSuite(test_to_run))
    return test_suite

mySuite = suite()

runner = unittest.TextTestRunner()
runner.run(mySuite)

