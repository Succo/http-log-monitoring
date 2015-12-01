#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time
import random
from datetime import datetime, timezone
import threading
import curses

def lineGenerator():
    """ Function to generate fake line similar to http log
    For now only time andsection are important to addapt
    """
    # List of random section to pick from
    sectionList = [
        '/js',
        '/img',
        '/css',
        '/',
        '/videos',
        '/http-bind',
        '/skins',
        '/plugins',
        '/piwik',
        '/program',
        '/users',
        '/directs',
        '/load.php',
        '/favicon.ico',
        '/index.php',
        '/fonticons',
        '/robots.txt',
        '/categories',
        '/pages',
        '/resources',
        '/images',
        '/nxmen'
    ]
    queryList = [
        "_task=mail",
        "_remote=1",
        "_unlock=0",
        "_action=getunread",
        "_task=mail",
        "_refresh=1",
        "_mbox=INBOX",
        "_remote=1",
        "_unlock=loading1447574840064",
        "_action=list",
        "_=1447574839937"
    ]
    line =  "127.0.0.1 - - ["
    date = datetime.now(timezone.utc).strftime("%d/%b/%Y:%H:%M:%S %z")
    line += date +'] "GET '
    section = random.choice(sectionList)
    for i in range(random.randrange(3)):
        if (i == 0):
            section += "?"
        else:
            section += "&"
        section+= random.choice(queryList)
    line += section +' HTTP/1.1" '
    if (random.randrange(21)>19):
        line += '404 '
    else:
        line += '200 '
    line += str(random.randrange(3000, 7000))
    line += ' "-" ""Mozilla/5.0 (compatible; pythonLogGenerator/0.1)""\n'
    return line

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates fake http log to a file for testing purposes')

    parser.add_argument('filenames', metavar='log files', nargs='+', help='Files where to generate fake logs')
    args = parser.parse_args()

    # Rate is the number of log entry by seconds (default 1)
    # No need to add a lock for it as one thread only execute atomic operation on it
    # and doesn't update it
    rate = 1

    # We uses cures for esthetics and key detection
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

    stdscr.addstr(1,1,'Writing fake http log to ' + str(args.filenames))
    stdscr.addstr(2,1,'Hit q to interrupt')
    stdscr.addstr(3,1, 'Press I to increase rate and D to decrease')
    stdscr.addstr(4,1, 'Actual rate is ' + str(rate) + ' per second')

    def updateLog():
        """ A function to continously update the log
        needs to be run in a thread
        """
        global rate
        while True:
            for filePath in args.filenames:
                with open(filePath, 'a') as file:
                    for k in range(rate):
                        file.write(lineGenerator())
                    time.sleep(1)

    def watchKeyPress():
        """A function to check for key press and act upon them
        needs to be run in the main thread
        """
        global rate, stdscr
        while True:
            key = stdscr.getkey()
            if (key == 'q'):
                # only return on q
                return
            elif (key == 'i'):
                rate += 1
            elif ((key == 'd') and (rate > 0)):
                rate -= 1
            stdscr.move(4,0)
            stdscr.clrtoeol()
            stdscr.addstr(4,1, 'Actual rate is ' + str(rate) + ' per second')


    # We run the update log in it's own thread
    updateLogThread = threading.Thread(target=updateLog, daemon = True)
    updateLogThread.start()

    # We keep watching for key press
    watchKeyPress()

    # When the function return we can clean curse
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
