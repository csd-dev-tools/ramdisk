"""
If this script is run rather than used as a library, it will show how it can
be used to create a basic menu.

@author: Roy Nielsen
"""
from __future__ import absolute_import
# system libraries
import re
import sys
import tty
import termios

sys.path.append("..")
from lib.loggers import CrazyLogger
from lib.loggers import LogPriority as lp
from lib.run_commands import RunWith, runMyThreadCommand

class MenuComponent(object):
    """
    """
    def __init__(self, name, options=False):
        """
        """
        if isinstance(options, dict):
            self.g_dict = options
        else:
            self.g_dict = {}
        if isinstance(name, str):
            self.name = name
        else: 
            raise Exception("Need a valid name...")

        self.runner = RunWith()
        self.logger = CrazyLogger(debug_mode=True)
        self.logger.initializeLogs()
        
        self.action = False
        self.anchor = False

        self.run = runMyThreadCommand

    def menuAction(self):
        """
        """
        pass

    def get_key(self):
        """
        Wait for a keypress and return a single character string.

        If either of the Unix-specific tty or termios are not found
        we allow the ImportError to proagate..
        
        @author: unknown
        """
        fd = sys.stdin.fileno()
        original_attributes = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, original_attributes)
        return ch

    def get_value(self, g_key=False, g_value=None):
        """
        Get the value of a psudo-global value.  Not using python globals.
        Child classes should be able to look up these values, found in the
        MenuComposite with the Anchor (first MenuComponent)
        
        g_value is the name of the self.conf.get_<var-name> routine to get
                that variable

        Author: Roy Nielsen
        """
        retval = False
        if g_key and g_value is not None:
            while not self.anchor:
                self = self.previous
            try:
                retval = self.g_dict[g_key]
            except IndexError:
                print "Damn it Jim!!! Key: " + str(g_key) + " is missing..."

        return retval

    def set_value(self, g_key=False, g_value=None, type=None):
        """
        Set a value in the 'anchor' node of the menu.

        s_value is the name of the self.conf.set_<var-name> routine to set
                that variable.
        equals is the value we want to set to
        type is the type, either string of int

        Author: Roy Nielsen
        """
        success = False
        if not g_key and g_value is not None and type is not None:
            while not self.anchor :
                self = self.previous
                print self.name + " " + str(g_key) + " = " + \
                                        str(g_value) + ", " + \
                                        str(type)

            if isinstance(g_value, str(type)):
                self.g_dict[g_key] = g_value
                success = True

        return success

    def validateName(self, name=False):
        """
        """
        success = False
        if name:
            try:
                re.match("^[A-Za-z0-9]*", name)
            except:
                pass
            else:
                success = True

    def validateAction(self, action=False):
        """
        """
        success = False
        if action:
            try:
                re.match("^[A-Za-z0-9]*", str(action))
            except:
                pass
            else:
                success = True

        return success

    def print_name(self) :
        """
        Print the name of the MenuItem for the menu.

        Author: Roy Nielsen
        """
        print self.name


class MenuItem(MenuComponent) :
    """
    Leaf class - Inherits the MenuComponent class.

    Author: Roy Nielsen
    """
    def __init__(self, name, action=False) :
        """
        Initialization method.  Initialize the MenuComponent, then set the "name"
        of the menu item.
        """
        MenuComponent.__init__(self, name)
        print str(action)
        if action:
            if self.validateAction(action):
                self.action = action
        else:
            self.action()

    def menuAction(self):
        """
        Node specific action method. -- Run the function that is passed in.

        Author: Roy Nielsen
        """
        success = False
        if self.action:
            if self.validateAction(self.action):
                success = self.action()

            print self.name

        return success

        
class MenuComposite(MenuComponent) :
    """
    Composite method found in the link above.  This controls a menu level.

    @author: Roy Nielsen
    """
    def __init__(self, name, action=False) :
        """
        Initialization method.

        @author: Roy Nielsen
        """
        MenuComponent.__init__(self, name)
        if self.validateAction(action):
            self.action = action
        self.child_nodes = []

        self.print_name()

    def menuAction(self) :
        """
        Create the menu - execute the exec string first if it's not empty.

        Print each MenuItem of this MenuComposite in order,

        @author: Roy Nielsen
        """
        success = False

        #####
        # If the action parameter
        if self.action:
            success = self.action()

        self.logger.log(lp.DEBUG, "Action returns success: " + str(success))

        #####
        # Print the menu and act on the menu selection
        while True :
            # print out the menu item
            #self.runner.setCommand("/usr/bin/clear")
            #self.runner.wait()
            #self.run(["/usr/bin/clear"], self.logger)
            print "\033c"
            #curses.initscr().clear()
            #win.refresh()
            print "\n" + self.name + " Menu\n"
            i = 1
            for item in self.child_nodes :
                print "[" + str(i) + "] " + self.child_nodes[(i-1)].name
                i = i + 1
            if not self.anchor :
                print "[" + str(i) + "] Return to " + \
                      self.previous.name + \
                      " Menu"
                print "[" + str(i+1) + "] Quit"
            else :
                print "[" + str(i) + "] Quit"

            print "\nSelect an option and hit Enter"

            # get input from the command line
            enter = sys.stdin.readline()

            # Figure out which number (or [Q|q] they hit
            if re.match("^\d+$", enter) :
                enter = int(enter)
            elif re.match("^[Qq]$", enter) :
                try :
                    sys.exit()
                except OSError, err :
                    self.logger.log(lp.DEBUG, "OSError on attempt to exit: " + \
                                    str(err))
            else :
                continue
            
            # go back to the previous menu    
            if enter == (len(self.child_nodes)+1) :
                break

            # Either quit, or execute the "execute" method of the MenuItem, or
            # MenuComposite
            if enter == (len(self.child_nodes)+ 2) and not self.anchor:
                try :
                    sys.exit()
                except OSError, err :
                    self.logger.log(lp.DEBUG, "OSError on attempt to exit: " + \
                                    str(err))
                                    
            elif enter >= 0 and enter <= len(self.child_nodes) :
                self.child_nodes[(enter-1)].menuAction()
            else :
                continue


    def appendChild(self, child) :
        """
        Append child to self's child nodes - IE: Add a MenuItem or MenuComposite
        to the current MenuComposite
        
        For this "menu" system, no "remove" method necessary
        
        Author: Roy Nielsen
        """
        self.child_nodes.append(child)
        child.previous = self
        child.current = child


    def set_anchor(self) :
        """
        Set this MenuComposite as the "anchor" or "head" of the tree
        
        Author: Roy Nielsen
        """
        self.anchor = True


def basic():
    """
    """
    print "You have chosen a basic choice"
    print "Press any key to continue"
    # get input from the command line
    sys.stdin.readline()
    
def advanced1():
    """
    """
    print "You have chosen the first advanced option"
    print "Press any key to continue"
    # get input from the command line
    sys.stdin.readline()
    
def advanced2():
    """
    """
    print "You have chosen the second advanced option"
    print "Press any key to continue"
    # get input from the command line
    sys.stdin.readline()
    
def advanced3():
    """
    """
    print "You have chosen the third advanced option"
    print "Press any key to continue"
    # get input from the command line
    sys.stdin.readline()
    

if __name__ == "__main__" :
    """
    Example usage of this library
    
    @author: Roy Nielsen
    """
    main_menu = MenuComposite("Main")
    basic_choice = MenuItem("Basic Choice", basic)
    advanced_choice = MenuComposite("Advanced Choice")

    main_menu.set_anchor()

    main_menu.appendChild(basic_choice)
    main_menu.appendChild(advanced_choice)

    child1 = MenuItem("First advanced option", advanced1)
    child2 = MenuItem("Second advanced option", advanced2)
    child3 = MenuItem("Third advanced option", advanced3)

    advanced_choice.appendChild(child1)
    advanced_choice.appendChild(child2)
    advanced_choice.appendChild(child3)

    ##########
    # Call main menu
    main_menu.menuAction()
    
    print "---------------------------------------"
    print "======================================="
    print "### Ready To Work...                ###"
    print "======================================="
    print "---------------------------------------"

