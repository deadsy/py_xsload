# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Utilities - small helper functions
"""
#------------------------------------------------------------------------------

import sys
import array

#------------------------------------------------------------------------------

def unparen(x):
    """convert "(hex-number)" to integer"""
    return int(x[1:-1], 16)

#------------------------------------------------------------------------------

def b2s(b):
    """convert bytes to a string"""
    return array.array('B', b).tostring()

#------------------------------------------------------------------------------

def reverse8(x):
    """reverse a byte"""
    x = ((x & 0xaa) >> 1) | ((x & 0x55) << 1)
    x = ((x & 0xcc) >> 2) | ((x & 0x33) << 2)
    x = ((x & 0xf0) >> 4) | ((x & 0x0f) << 4)
    return x

#------------------------------------------------------------------------------

class progress:
    """percent complete and activity indication"""

    def __init__(self, div, size):
        """
        progress indicator
        div = slash speed
        nmax = maximum value, 100%
        """
        self.size = size
        self.n = 0
        self.inc = size / div
        self.progress = ''

    def erase(self):
        """erase the progress indication"""
        n = len(self.progress)
        sys.stdout.write(''.join(['\b' * n, ' ' * n, '\b' * n]))

    def update(self, n):
        """update the progress indication"""
        if n > (self.n * self.inc):
            self.n += 1
            self.erase()
            istr = '-\\|/'[self.n & 3]
            pstr = '%d%% ' % ((100 * n) / self.size)
            self.progress = ''.join([pstr, istr])
            sys.stdout.write(self.progress)
            sys.stdout.flush()

#------------------------------------------------------------------------------

