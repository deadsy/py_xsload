# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Definitions and functions specific to the Xilinx Spartan FPGAs
"""
#-----------------------------------------------------------------------------

import bitfile

#-----------------------------------------------------------------------------

class xc3s1000:

    def __init__(self, smap):
        self.smap = smap

    def configure(self, filename):
        """configure the device with a bit file"""
        print('configuring fpga with %s' % filename)
        f = bitfile.bitfile(filename, self.smap)
        f.load()

#-----------------------------------------------------------------------------

