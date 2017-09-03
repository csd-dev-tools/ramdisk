import os
import re
import unittest
from lib.loggers import CyLogger
from lib.run_commands import RunWith

dirPkgRoot = '.'
logger = CyLogger()
logger.initializeLogs()
rw = RunWith(logger)
pylint = "/usr/local/bin/pylint"
 
def gen_test_data():
    test_case_data = []
    for root, dirs, files in os.walk(dirPkgRoot):
        for myfile in files:
            if re.search(".+\.py$", myfile): # and not re.match("^%s$"%__file__, myfile):
                rw.setCommand([pylint, os.path.join(root, myfile)])
                output, error, retcode = rw.communicate()
                for line in output.split("\n"):
                    try:
                        info = re.match("^E:\s+(\d+),\s+\d+:\s+(.*)", line)
                        lineNum = info.group(1)
                        text = info.group(2)
                        test_case_data.append((os.path.join(root, myfile), lineNum, text)) 
                    except:
                        pass
                for line in error.split("\n"):
                    try:
                        info = re.match("^E:\s+(\d+),\s+\d+:\s+(.*)", line)
                        lineNum = info.group(1)
                        text = info.group(2)
                        test_case_data.append((os.path.join(root, myfile), lineNum, text)) 
                    except:
                        pass
    return test_case_data

test_case_data = gen_test_data()

def pylint_test_template(*args):
    '''
    decorator for monkeypatching
    '''
    def foo(self):
        self.assert_pylint_error(*args)
    return foo


class PylintTest(unittest.TestCase):
    def assert_pylint_error(self, myfile, lineNum, text):
        self.assertTrue(False, myfile + ": (" + str(lineNum) + ") " + text)

for specificError in test_case_data:
    myfile, lineNum, text = specificError
    test_name = "test_with_pylint_{0}_{1}".format(myfile, lineNum)
    error_case = pylint_test_template(*specificError)
    setattr(PylintTest, test_name, error_case)

