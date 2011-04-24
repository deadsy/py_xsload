# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Definitions and functions specific to the XSA3S1000 board
See - http://www.xess.com/prods/prod035.php
"""
#-----------------------------------------------------------------------------

import bitbang
import pport
import jtag
import xc9500

#-----------------------------------------------------------------------------

class Error(Exception):
    pass

#-----------------------------------------------------------------------------
# map the cpld jtag pins to the parallel port

_CPLD_TCK = (1 << 1) # parallel port c1 - pin 14
_CPLD_TMS = (1 << 2) # parallel port c2 - pin 16
_CPLD_TDI = (1 << 3) # parallel port c3 - pin 17
_CPLD_TDO_BIT = 7    # parallel port S7 - pin 11

class cpld_jtag:

    def __init__(self, io):
        self.io = io
        self.io.wr_data(0)

    def jtag_out(self, tck, tms, tdi = 0):
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
        return ((self.io.rd_status() >> _CPLD_TDO_BIT) & 1) ^ 1

    def __str__(self):
        return '%s (xsa3s1000)' % str(self.io)

#-----------------------------------------------------------------------------

class board:

    def __init__(self, itf = None):
        # TODO - itf - interface selection
        pass

    def cpld_init(self):
        """setup the cpld access"""
        driver = bitbang.jtag_driver(cpld_jtag(pport.io(0)))
        chain = jtag.chain(0, driver)
        chain.scan()
        # the cpld should be the 1 and only device on the chain
        if len(chain.devices) != 1:
            raise Error, 'wrong number of devices on cpld jtag chain (is %d, expected 1)' % len(chain.devices)
        device = chain.devices[0]
        # check the cpld idcode
        if device.idcode != jtag.IDCODE_XC9572XL:
            raise Error, 'wrong idcode for cpld (is 0x%08x, expected 0x%08x)' % (device.idcode, jtag.IDCODE_XC9572XL)
        self.cpld = xc9500.xc9500(chain, device)

    def __str__(self):
        return str(self.cpld)

#-----------------------------------------------------------------------------