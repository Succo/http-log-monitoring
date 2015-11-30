import curses
import threading
import time

class DisplayManager():
    """This class serves to display
    data on screen it uses curses
    """

    def __init__(self, parser, updatingDataLock):
        """ Initialise the curse application
        """
        self.stdscr = curses.initscr()
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

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
        self.data = parser.data
        # We also keep a reference to the thresholds as it serve to know which way we crossed it
        self.THRESHOLDS = parser.THRESHOLDS

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

    def readableByte(self, byte):
        """ Return an human readable string
         of the byte given in  entry (approximate)
         """
        suffixes = ["bytes","KB","MB","GB"]
        byte = float(byte)
        for suffixe in suffixes:
            if (byte < 1024):
                return str(round(byte, 2)) + " " + suffixe
            else:
                 byte = byte/1024.0

    def display(self):
        """ Updates the display with new data
        """
        # We try to acquire the lock to make the data are not being updated
        self.updatingDataLock.acquire()

        self.statWindow.clear()

        # serves as a line counter for text printing
        y = 0
        # To reduce code cruft
        result = self.data["shortTerm"]["sectionResult"]

        # This functions serve to remove one loop of data processing
        # sorted second argument must be a function returning a comparison key
        # so we need this function to do so
        def lengthFromKey(x):
            return len(result.get(x))

        for section in sorted(result, key= lengthFromKey, reverse=True):
            # print the section name followed by the number of view
            self.statWindow.addstr(y,0,"The section ")
            self.statWindow.addstr(section, curses.color_pair(2))
            self.statWindow.addstr(" has " + str(len(result.get(section))) + " view")
            # update line count
            y += 1

        self.statWindow.addstr(y,0,"Data served in the last 10s: ")
        self.statWindow.addstr(self.readableByte(self.data["shortTerm"]["contentServed"]), curses.color_pair(3))
        y += 1

        if (self.data["shortTerm"]["failedRequest"] > 0):
            self.statWindow.addstr(y,0,"In the last 10s there were ")
            self.statWindow.addstr(str(self.data["shortTerm"]["failedRequest"]), curses.color_pair(3))
            self.statWindow.addstr(" badly formed request")
            y += 1

        self.statWindow.addstr(y,0,"Total number of request in the last 2 min: ")
        self.statWindow.addstr(str(sum(self.data["longTerm"])), curses.color_pair(3))
        y += 1

        for numberOfHits, alertTime in self.data["alert"]:
            if (numberOfHits > self.THRESHOLDS):
                self.statWindow.addstr(y,0, "High traffic generated an alert - ")
                self.statWindow.addstr("hits = " + str(numberOfHits),curses.color_pair(1))
                self.statWindow.addstr(", triggered at ")
                self.statWindow.addstr(alertTime.strftime("%H:%M:%S"), curses.color_pair(3))
            else:
                self.statWindow.addstr(y,0, "Traffic back to normal at ")
                self.statWindow.addstr(alertTime.strftime("%H:%M:%S"), curses.color_pair(3))
            y += 1

        self.statWindow.refresh()
        self.updatingDataLock.release()
        return
