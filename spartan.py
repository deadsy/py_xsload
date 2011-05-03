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
        bitfile.load(filename, self.smap)

#-----------------------------------------------------------------------------

class xc3s200a:

    def __init__(self, jtag):
        self.jtag = jtag

    def __str__(self):
        s = []
        s.append(str(self.jtag))
        return '\n'.join(s)

#-----------------------------------------------------------------------------

