#!/usr/bin/python
'''
Runs pylint on all python .py files in a directory tree

@author: Roy Nielsen
'''
from __future__ import absolute_import

import re
import os
import sys
import unittest

#sys.path.append("..")

from ..lib.CheckApplicable import CheckApplicable
from ..lib.environment import Environment
from ..lib.run_commands import RunWith
from ..lib.loggers import CyLogger
from ..lib.loggers import LogPriority as lp

class test_with_pylint(unittest.TestCase):
    """
    """
    @classmethod
    def setUpClass(self):
        """
        """
        pass

    def setUp(self):
        """
        """
        self.environ = Environment()
        self.logger = CyLogger()
        self.logger.initializeLogs()
        self.rw = RunWith(self.logger)
        macApplicable = {'type' : 'white', 'os' : {'Mac OS X': ['10.10', 'r', '10.13.10']}}
        linuxApplicable = {'type' : 'white', 'family': 'linux'}

        chkApp = CheckApplicable(self.environ, self.logger)
        if chkApp.isApplicable(macApplicable):
            self.pylint = "/usr/local/bin/pylint"

        self.dirPkgRoot = '..'

    def test_for_errors(self):
        """
        """
        for root, dirs, files in os.walk(self.dirPkgRoot):
            for myfile in files:
                if re.search(".+\.py$", myfile) and not re.match("^%s$"%__file__, myfile):
                    self.rw.setCommand([self.pylint, os.path.join(root, myfile)])
                    output, error, retcode = self.rw.communicate()
                    for line in output.split("\n"):
                        if re.match("^E:.+", line):
                            self.assertTrue(False, str(os.path.join(root, myfile)) + " has error: " + str(line))
                    for line in error.split("\n"):
                        if re.match("^\s*E:\s+.+", line):
                            self.assertTrue(False, str(os.path.join(root, myfile)) + " has error: " + str(line))
        self.assertTrue(True, "...")
    """
    def test_for_warnings(self):
        ""
        ""
        for root, dirs, files in os.walk(self.dirPkgRoot):
            for myfile in files:
                if re.search(".+\.py$", myfile):
                    self.rw.setCommand([self.pylint, os.path.join(root, myfile)])
                    output, error, retcode = self.rw.communicate()
                    for line in output.split("\n"):
                        if re.match("^W:.+", line):
                            self.assertTrue(False, str(myfile) + " has error: " + str(line))
                    for line in error.split("\n"):
                        if re.match("^\s*W:\s+.+", line):
                            self.assertTrue(False, str(myfile) + " has error: " + str(line))
        self.assertTrue(True, "...")
    """

    @classmethod
    def tearDownClass(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass
