# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Bitfile Loader
"""
#------------------------------------------------------------------------------

import time
import os

import utils
import bits

#------------------------------------------------------------------------------

class Error(Exception):
    pass

#------------------------------------------------------------------------------

class bitfile:

    def __init__(self, filename, smap):
        self.filename = filename
        self.smap = smap

    def load(self):
        pass

#------------------------------------------------------------------------------