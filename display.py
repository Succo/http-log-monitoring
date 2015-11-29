import curses
import threading
import time

class DisplayManager():
    """This class serves to display
    data on screen it uses curses
    """

    def __init__(self, sectionResult, updatingDataLock):
        """ Initialise the curse application
        """
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)
        maxY, maxX = self.stdscr.getmaxyx()
        self.stdscr.addstr(maxY-1,0,"Http log parsing program - type anykey to exit")

        # We create a window where all the stats will be printed
        # this way we can redraw only part of the screen every 10s
        self.statWindow = self.stdscr.subwin(maxY-2, maxX, 0, 0)

        # We keep a reference to the lock
        self.updatingDataLock = updatingDataLock

        # We keep a reference to the result generated (and updated) by the parser
        self.sectionResult = sectionResult

        def displayManager(display):
            """ A function to call in loop
            display and update it
            """
            while True:
                display()
                time.sleep(1)

        # We define a thread to call to update the display
        self.display = threading.Thread(target=displayManager, args= (self.display,), daemon = True)
        return

    def clearCurse(self):
        """ Clean the curse application
        """
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        return

    def display(self):
        """ Updates the display with new data
        """
        # We try to acquire the lock to make the data are not being updated
        self.updatingDataLock.acquire()

        self.statWindow.clear()
        # This functions serve to remove one loop of data processing
        # sorted second argument must be a function returning a comparison key
        # so we need this function to do so
        def lengthFromKey(x):
            return len(self.sectionResult.get(x))

        # serves as a line counter for text printing
        y = 0
        for section in sorted(self.sectionResult, key= lengthFromKey, reverse=True):
            # print the section name followed by the number of view
            self.statWindow.addstr(y,0,"The section " + section + " has " + str(len(self.sectionResult.get(section))) + " view")
            # update line count
            y += 1
        self.statWindow.refresh()
        self.updatingDataLock.release()
        return
