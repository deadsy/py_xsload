# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Definitions and functions specific to the XuLA board
See - http://www.xess.com/prods/prod048.php
"""
#-----------------------------------------------------------------------------

import jtag
import xsusb

#-----------------------------------------------------------------------------

class board:

    def __init__(self, itf = None):
        # TODO - itf - interface selection
        # setup the fpga access
        chain = jtag.jtag(xsusb.jtag_driver(0))



    def __str__(self):
        s = []
        s.append('XuLA Board')
        return '\n'.join(s)

#-----------------------------------------------------------------------------
