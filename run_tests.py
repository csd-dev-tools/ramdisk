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
from optparse import OptionParser, SUPPRESS_HELP, OptionValueError, Option

testdir = "./tests"
sys.path.append(testdir)

###############################################################################

class BuildAndRunSuite(object):

    def __init__(self):
        """
        """
        self.module_version = '20160224.032043.009191'
        self.prefix=[]

    ##############################################

    def setPrefix(self, prefix=[]):
        """
        Setter for the prefix variable...
        """
        if prefix and isinstance(prefix, list):
            self.prefix = prefix
        else:
            self.prefix=["test_"]

    ##############################################

    def get_all_tests(self, prefix=[]):
        """
        Collect all available tests using the test prefix(s)

        @author: Roy Nielsen
        """
        if not self.modules:
            test_list = []
            allfiles = os.listdir(testdir)
            for check_file in allfiles:
                test_name = str(check_file).split(".")[0]
                pycfile = os.path.join("./tests/", test_name + ".pyc")
                if os.path.exists(pycfile):
                    os.unlink(pycfile)
                elif re.match("^test_.+.py$", check_file):
                    print "Loading test: " + str(check_file)
                    test_list.append(os.path.join("./tests/", check_file))
            print str(test_list)

        return test_list

    ##############################################

    def run_suite(self, modules=[]):
        """
        Gather all the tests from this module in a test suite.

        @author: Roy Nielsen
        """
        self.test_dir_name = testdir.split("/")[1]
        self.modules = modules

        #####
        # Initialize the test suite
        self.test_suite = unittest.TestSuite()

        #####
        # Generate the test list
        if self.modules and isinstance(self.modules, list):
            test_list = self.modules
        else:
            test_list = self.get_all_tests(prefix)

        #####
        # Import each of the tests and add them to the suite
        for check_file in test_list:
            print str(check_file)
            test_name = str(check_file).split("/")[-1]
            test_name = str(test_name).split(".")[0]
            print "test_name: " + str(test_name)
            test_name_import_path = "." + ".".join([self.test_dir_name, test_name])
            print "test_name_import_path: " + str(test_name_import_path)

            ################################################
            # Test class needs to be named the same as the
            #   filename for this to work.
            # import the file named in "test_name" variable
            test_to_run = __import__(test_name)
            # getattr(x, 'foobar') is equivalent to x.foobar
            test_to_run = getattr(test_to_run, test_name)
            # Add the test class to the test suite
            self.test_suite.addTest(unittest.makeSuite(test_to_run))

        #####
        # calll the run_action to execute the test suite
        self.run_action()

    ##############################################

    def run_action(self):
        """
        Run the Suite.
        """
        runner = unittest.TextTestRunner()
        runner.run(self.test_suite)

###############################################################################

# Get all of the possible options passed in to OptionParser that are passed
# in with the -m or --modules flag
class ModulesOption(Option):

    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            lvalue = value.split(",")
            values.ensure_value(dest, []).extend(lvalue)
        else:
            Option.take_action(
                self, action, dest, opt, value, values, parser)

###############################################################################

if __name__ == "__main__":
    """
    Executes if this file is run.
    """

    VERSION="0.4.0"
    description = "Generic test runner."
    parser = OptionParser(option_class=ModulesOption,
                          usage='usage: %prog [OPTIONS]',
                          version='%s' % (VERSION),
                          description=description)

    parser.add_option("-a", "--all-automatable", action="store_true", dest="all",
                      default=False, help="Run all tests except interactive tests.")

    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", default=False, \
                      help="Print status messages")

    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="Print debug messages")

    parser.add_option('-p', '--prefix', action="extend", type="string",
                      dest='prefix', default=[],
                      help="Collect tests with these prefixes.")

    parser.add_option('-m', '--modules', action="extend", type="string",
                      dest='modules', default=[], help="Use to run a single or " + \
                      "multiple unit tests at once.  Use the test name.")

    if len(sys.argv) == 1:
        parser.parse_args(['--help'])

    options, __ = parser.parse_args()

    #####
    # Options processing

    #####
    # ... processing modules ...
    if options.all:
        modules = None
    elif options.modules:
        modules = options.modules

    print "Modules: " + str(modules)

    #####
    # ... processing logging options...
    verbose = options.verbose
    debug = options.debug

    #####
    # ... processing test prefixes
    if options.prefix:
        prefix = options.prefix
    else:
        prefix = ["test_"]


    bars = BuildAndRunSuite()
    bars.run_suite(modules)
