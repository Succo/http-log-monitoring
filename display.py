#import curses
import curses

class DisplayManager():
    """This class serves to display
    data on screen it uses curses
    """

    def __init__(self):
        """ Initialise the curse application
        """
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def clearCurse(self):
        """ Clean the curse application
        """
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def display(self, parsedData):
        """ Updates the display with new data
        """
        self.stdscr.clear()
        # This functions serve to remove one loop of data processing
        # sorted second argument must be a function returning a comparison key
        # so we need this function to do so
        def lengthFromKey(x):
            return len(parsedData.get(x))

        # serves as a line counter for text printing
        y = 0
        for section in sorted(parsedData, key= lengthFromKey, reverse=True):
            # print the section name followed by the number of view
            self.stdscr.addstr(y,0,"The section " + section + " has " + str(len(parsedData.get(section))) + " view")
            # update line count
            y += 1
        self.stdscr.refresh()
        return
