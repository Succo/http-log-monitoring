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


        # We keep a reference to the result generated (and updated) by the parser
        self.data = parser.data
        # We also keep a reference to the thresholds as it serve to know which way we crossed it
        self.THRESHOLDS = parser.THRESHOLDS
        # We keep a reference to the lock
        self.updatingDataLock = updatingDataLock

        def displayManager(display):
            """ A function to call in loop
            display and update it
            """
            while True:
                display()
                time.sleep(1)

        self.initialiseCurse()

        # We define a thread to call to update the display
        self.display = threading.Thread(target=displayManager, args= (self.display,), daemon = True)
        return

    def initialiseCurse(self):
        """ This function will generate the different boxes needed
        for the application starting with stdcr
        """
        # We define option to add color
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        # Basic window setup, informative text at the bottom
        # and a big box
        self.stdscr.keypad(True)
        maxY, maxX = self.stdscr.getmaxyx()
        self.stdscr.addstr(maxY-1,1,"Http log parsing program - type anykey to exit")
        # This is the main window of the program, only defined to add a border
        windowBorder = self.stdscr.subwin(maxY-1, maxX, 0, 0)
        windowBorder.border()

        # We create a window where all the stats will be printed
        # That's the inside on the previous one
        generalDisplay = windowBorder.derwin(maxY-2, maxX-1, 0, 0)

        shortTermStatY, shortTermStatX = (9, min(maxX-2, 95))

        # This is the window where we will display data on the latest 10s
        # We prefill it with the imutable text
        shortTermStatWindow = generalDisplay.derwin(shortTermStatY, shortTermStatX, 1, 1)
        shortTermStatWindow.border()

        # serves as a line counter for text printing, so I can add new line easily
        y = 0

        # We first print the base text
        shortTermStatWindow.addstr(y,3,"Data from the latest 10s: ")
        y += 2
        # The section and query data structure are identical so we can use the same code to display both
        for text in ["section", "query"]:
            # print the section name followed by the number of view
            shortTermStatWindow.addstr(y,3,"The most requested "+ text +" :")
            # update line count
            y += 1

        y += 1
        shortTermStatWindow.addstr(y, 3,"Total data served: ")
        y += 1
        shortTermStatWindow.addstr(y, 3,"Failed request: ")

        # We need to position the three next columm, knowing that
        # - the section/query needs at most 15 letter
        # - the two other require 4 character plus 5 and 7 for two string ("Hit :" and "Total :")
        # - we must account for the last line
        #  the end result must look like
        #  30 character | space | 15 | space |Hit :....| space |Total :....|1 = last line
        # space = int((shortStatWidth -(30 + 15 + ( 4 + 5 ) + (7 + 4))/3)
        shortStatHeigh, shortStatWidth = shortTermStatWindow.getmaxyx()
        space = int((shortStatWidth -(66))/3)

        # We can now place the base text
        for y in range(2,4):
            shortTermStatWindow.addstr(y,2*space + 45,"Hit: ")
            shortTermStatWindow.addstr(y,3*space + 54,"Total: ")
        # We can also define the column that won't be immutable,
        # they are contained in the previous and are where stats from the log will go
        self.firstColumn = shortTermStatWindow.derwin(shortStatHeigh-2, 15, 1, space+30)
        self.secondColumn = shortTermStatWindow.derwin(shortStatHeigh-2, 4, 1, 2*space + 50)
        self.thirdColumn = shortTermStatWindow.derwin(shortStatHeigh-2, 4, 1, 3*space + 61)

        # Now we generate a new window for the data on the last 2 minutes
        longTermStatY, longTermStatX = (5, min(maxX-2, 95))

        # We prefill it with the imutable text
        longTermStatWindow = generalDisplay.derwin(longTermStatY, longTermStatX, shortTermStatY + 1, 1)
        longTermStatWindow.border()

        # serves as a line counter for text printing, so I can add new line easily
        y = 0

        # We first print the base text
        longTermStatWindow.addstr(y,3,"Data from the latest 2min: ")
        y += 2
        longTermStatWindow.addstr(y,3,"Total number of view: ")

        # We just need one column for this block
        self.longTermColumn = longTermStatWindow.derwin(longTermStatY-2, longTermStatX-space-31, 1, space+30)

        # Now we generate a new window for the alerts
        # the Y dimension is all that's left to display the maximun amount of alert possible
        alertY, alertX = (maxY- longTermStatY - shortTermStatY -3, min(maxX-2, 95))

        # We prefill it with the imutable text
        alertWindow = generalDisplay.derwin(alertY, alertX,  longTermStatY + shortTermStatY + 1, 1)
        alertWindow.border()

        # serves as a line counter for text printing, so I can add new line easily
        y = 0

        # We first print the base text
        alertWindow.addstr(y,3,"Alert status: ")

        # We just need one column for this block
        # Be careful this Column overlapse the top row
        # So we must not update the first line
        self.alertColumn = alertWindow.derwin(alertY-1, alertX-11, 0, 1)
        self.alertDateColumn = alertWindow.derwin(alertY-2, 9, 1, alertX-10)


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

        self.firstColumn.clear()
        self.secondColumn.clear()
        self.thirdColumn.clear()
        self.longTermColumn.clear()
        self.alertDateColumn.clear()

        # We first fill the data from the shortTermStatWindow (first,second and third columm)
        # serves as a line counter for text printing
        y = 1
        # The section and query data structure are identical so we can use the same code to display both
        for text in ["section", "query"]:
            # To reduce code cruft
            result = self.data["shortTerm"][text + "Result"]

            if (len(result) != 0):
                section = max(result, key=result.get)
                # Add text to the emplacement
                self.firstColumn.addstr(y, 0, section, curses.color_pair(3))
                self.secondColumn.addstr(y, 0, str(result.get(section)), curses.color_pair(2))
                self.thirdColumn.addstr(y, 0, str(sum(result.values())), curses.color_pair(2))
            # update line count
            y += 1

        y += 1
        self.firstColumn.addstr(y, 0,self.readableByte(self.data["shortTerm"]["contentServed"]), curses.color_pair(3))
        y += 1

        if (self.data["shortTerm"]["failedRequest"] > 0):
            self.firstColumn.addstr(y, 0, str(self.data["shortTerm"]["failedRequest"]), curses.color_pair(1))
        else:
            self.firstColumn.addstr(y, 0,"0", curses.color_pair(2))

        # Stats in the long term window
        self.longTermColumn.addstr(1, 0, str(sum(self.data["longTerm"])), curses.color_pair(3))

        # Stats in the alarm
        if ((len(self.data["alert"]) == 0) or (self.data["alert"][len(self.data["alert"])-1][0] < self.THRESHOLDS)):
                self.alertColumn.addstr(0 , 15, " OK  ", curses.color_pair(2))
        else:
                self.alertColumn.addstr(0 , 15, " NOK ",curses.color_pair(1))

        alert = self.data["alert"]
        alertY, alertX = self.alertColumn.getmaxyx()

        # We want to print the log from y = 1 to y = alertY finishing with the latest
        y = min(len(alert), alertY-1)
        if y < len(alert):
            alert = alert[len(alert)-y:]

        for numberOfHits, alertTime in alert:
            if(y>0):
                # We move the cusor to be able to call clrtoeol
                self.alertColumn.move(y,0)
                self.alertColumn.clrtoeol()
                if (numberOfHits > self.THRESHOLDS):
                    self.alertColumn.addstr(y,0, "High traffic generated an alert - ")
                    self.alertColumn.addstr("hits = " + str(numberOfHits),curses.color_pair(1))
                    self.alertColumn.addstr(", triggered at :")
                    self.alertDateColumn.addstr(y-1, 0,alertTime.strftime("%H:%M:%S"), curses.color_pair(3))
                else:
                    self.alertColumn.addstr(y,0, "Traffic back to normal at :")
                    self.alertDateColumn.addstr(y-1, 0,alertTime.strftime("%H:%M:%S"), curses.color_pair(3))
                y -= 1

        self.firstColumn.refresh()
        self.secondColumn.refresh()
        self.thirdColumn.refresh()
        self.longTermColumn.refresh()
        self.alertColumn.refresh()
        self.alertDateColumn.refresh()

        self.updatingDataLock.release()
        return
