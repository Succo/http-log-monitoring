#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# Clint used to handle command line arguments
# TODO get rid of it, as it is underused
from clint.arguments import Args
from clint.textui import puts, colored, indent

#import curses
from curses import wrapper

#Custom classes
from parser import LogParser
from display import DisplayManager

def main(stdscr):
    parser = LogParser(Args().files)
    displayManager = DisplayManager(stdscr)
    displayManager.display(parser.parse())



if __name__ == '__main__':
    wrapper(main)
