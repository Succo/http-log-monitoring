#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time

# Clint used to handle command line arguments
# TODO get rid of it, as it is underused
from clint.arguments import Args
from clint.textui import puts, colored, indent

#Custom classes
from parser import LogParser
from display import DisplayManager

import threading

if __name__ == '__main__':
    # This lock serve too avoid reading data when the parser is updating them
    updatingDataLock = threading.Lock()
    parser = LogParser(Args().files, updatingDataLock)
    displayManager = DisplayManager(parser ,updatingDataLock)
    parser.parse.start()
    displayManager.display.start()
    displayManager.stdscr.getch()
    displayManager.clearCurse()
