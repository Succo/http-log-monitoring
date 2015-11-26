#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# Clint used to handle command line arguments
# TODO get rid of it, as it is underused
from clint.arguments import Args
from clint.textui import puts, colored, indent

#Custom classes
from parser import LogParser
from display import DisplayManager

if __name__ == '__main__':
    parser = LogParser(Args().files)
    displayManager = DisplayManager()
    displayManager.display(parser.parse())
    displayManager.clearCurse()
