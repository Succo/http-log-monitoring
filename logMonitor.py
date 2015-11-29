#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import threading
import argparse

#Custom classes
from parser import LogParser
from display import DisplayManager

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parses http log files to generate useful stat')

    parser.add_argument('filenames', metavar='N', nargs='+', help='Files where are stocked http logs')
    args = parser.parse_args()

    # This lock serve too avoid reading data when the parser is updating them
    updatingDataLock = threading.Lock()
    parser = LogParser(args.filenames, updatingDataLock)
    displayManager = DisplayManager(parser ,updatingDataLock)
    parser.parse.start()
    displayManager.display.start()
    displayManager.stdscr.getch()
    displayManager.clearCurse()
