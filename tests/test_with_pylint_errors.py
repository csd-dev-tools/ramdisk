#!/usr/bin/python -u

from __future__ import absolute_import

import os
import re
import sys
import unittest

sys.path.append("..")

from lib.loggers import CyLogger
#from lib.run_commands import RunWith
from tests.PylintIface import PylintIface, processFile

from pylint import epylint

dirPkgRoot = '..'
logger = CyLogger()
logger.initializeLogs()
#rw = RunWith(logger)

def gen_test_data():
    test_case_data = []
    pIface = PylintIface(logger)
    for root, dirs, files in os.walk(dirPkgRoot):
        for myfile in files:
            #print file
            if re.search(".+\.py$", myfile): # and not re.match("^%s$"%__file__, myfile):
                output = ""
                error = ""
                jsonData = ""
                #print myfile
                jsonData = processFile(os.path.abspath(os.path.join(root, myfile)))
                jsonData = pIface.processFile(os.path.abspath(os.path.join(root, myfile)))
                #print jsonData
                for item in jsonData:
                    if re.match("^error$", item['type']) or re.match("^fatal$", item['type']):
                        #print "Found: " + str(item['type']) + " (" + str(item['line']) + ") : " + str(item['message'])
                        test_case_data.append((os.path.join(root, myfile), 
                                               item['line'], item['message'])) 
    #for data in test_case_data:
    #    print data
    return test_case_data

test_case_data = gen_test_data()

def pylint_test_template(*args):
    '''
    decorator for monkeypatching
    '''
    def foo(self):
        self.assert_pylint_error(*args)
    return foo


class test_with_pylint_errors(unittest.TestCase):
    def assert_pylint_error(self, myfile, lineNum, text):
        self.assertTrue(False, myfile + ": (" + str(lineNum) + ") " + text)

for specificError in test_case_data:
    #print str(specificError)
    myfile, lineNum, text = specificError
    test_name = "test_with_pylint_{0}_{1}_{2}".format(myfile, lineNum, text)
    error_case = pylint_test_template(*specificError)
    setattr(test_with_pylint_errors, test_name, error_case)

