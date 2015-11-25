#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from clint.arguments import Args
from clint.textui import puts, colored, indent
from parser import LogParser

if __name__ == '__main__':
    parser = LogParser(Args().files)
    stat = {}
    for section, list in parser.parse().items():
        stat[section] = len(list)
    for w in sorted(stat, key=stat.get, reverse=True):
        print(w, stat[w])
