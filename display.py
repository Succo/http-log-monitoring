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
        stat = {}
        # Count the nimber of view by section
        for section, list in parsedData.items():
            stat[section] = len(list)
        # serves as a line counter
        y = 0
        for w in sorted(stat, key=stat.get, reverse=True):
            # print the section name followed by the number of view
            self.stdscr.addstr(y,0,w + " ")
            self.stdscr.addstr(str(stat[w]))
            # update line count
            y += 1
        self.stdscr.refresh()
        self.stdscr.getkey()
        return
