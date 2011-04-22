# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Definitions and functions specific to the XSA3S1000 board
See - http://www.xess.com/prods/prod035.php
"""
#-----------------------------------------------------------------------------
# map the cpld jtag pins to the parallel port

_CPLD_TCK = (1 << 1) # parallel port c1 - pin 14
_CPLD_TMS = (1 << 2) # parallel port c2 - pin 16
_CPLD_TDI = (1 << 3) # parallel port c3 - pin 17
_CPLD_TDO = (1 << 7) # parallel port S7 - pin 11

class cpld:

    def __init__(self, io):
        self.io = io
        self.io.wr_data(0)

    def jtag_out(self, tck, tms, tdi):
        """set the tck, tms and tdi bits"""
        val = 0
        if not tck:
            val |= _CPLD_TCK
        if tms:
            val |= _CPLD_TMS
        if not tdi:
            val |= _CPLD_TDI
        self.io.wr_ctrl(val)

    def jtag_in(self):
        """get the tdo bit"""
        return (0, 1)[(self.io.rd_status() & _CPLD_TDO) == 0]

#-----------------------------------------------------------------------------

class board:

    def __init__(self):
        pass





#-----------------------------------------------------------------------------