# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Definitions and functions specific to the XuLA board
See - http://www.xess.com/prods/prod048.php
"""
#-----------------------------------------------------------------------------

import jtag
import xsusb
import utils
import spartan

#-----------------------------------------------------------------------------

class Error(Exception):
    pass

#-----------------------------------------------------------------------------

class board:

    def __init__(self, itf = None):
        # TODO - itf - interface selection
        self.xsusb = xsusb.xsusb(0)
        # setup the jtag interface
        chain = jtag.jtag(xsusb.jtag_driver(self.xsusb))
        chain.scan(jtag.IDCODE_XC3S200A)
        self.fpga = spartan.xc3s200a(chain)

    def __str__(self):
        s = []
        s.append(str(self.fpga))
        return '\n'.join(s)

#-----------------------------------------------------------------------------
