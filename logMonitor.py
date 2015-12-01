#!/usr/bin/env python3
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

    parser.add_argument('-t', '--threshold', metavar='threshold', type=int, default = 1000, help='The threshold of page served by 2min which will generate alarms')
    parser.add_argument('filenames', metavar='log files', nargs='+', help='Files where are stocked http logs')
    args = parser.parse_args()

    # This lock serve too avoid reading data when the parser is updating them
    updatingDataLock = threading.Lock()
    parser = LogParser(args.filenames, updatingDataLock, args.threshold)
    displayManager = DisplayManager(parser ,updatingDataLock)
    parser.parserManager.start()
    displayManager.displayManager.start()
    displayManager.stdscr.getch()
    displayManager.clearCurse()
