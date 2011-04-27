# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Utilities - small helper functions
"""
#------------------------------------------------------------------------------

import sys

#------------------------------------------------------------------------------

def unparen(x):
    """convert "(hex-number)" to integer"""
    return int(x[1:-1], 16)

#------------------------------------------------------------------------------

class progress:
    """percent complete and activity indication"""

    def __init__(self, inc, size):
        """
        progress indicator
        div = slash speed, larger is slower
        nmax = maximum value, 100%
        """
        self.size = size
        self.n = 0
        self.inc = inc
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

