#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from clint.arguments import Args
from clint.textui import puts, colored, indent
from parser import parse

if __name__ == '__main__':
    #print(parse(Args().files))
    parse(Args().files)
