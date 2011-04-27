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

_file_path = './bitfiles/XSA/3S1000/LPT/'

_cpld_files = (
    'dwnldpar.svf',
    'erase.svf',
    'fcnfg.svf',
    'p3jtag.svf',
    'p4jtag.svf',
)

_fpga_files = (
    'fintf.bit',
    'ramintfc.bit',
    'test_board.bit',
)

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

    def test_reset(self, val):
        """control the test reset line"""
        # don't have a ~trst line
        pass

    def __str__(self):
        return '%s (xsa3s1000 cpld)' % str(self.io)

#-----------------------------------------------------------------------------
# map the fpga jtag pins to the parallel port (needs p3jtag.svf in the cpld)

_FPGA_TDI = (1 << 0) # parallel port d0 - pin 2
_FPGA_TCK = (1 << 1) # parallel port d1 - pin 3
_FPGA_TMS = (1 << 2) # parallel port d2 - pin 4
_FPGA_OE  = (1 << 3) # parallel port d3 - pin 5 (active lo)
_FPGA_IE  = (1 << 4) # parallel port d4 - pin 6 (active hi)
_FPGA_TDO_BIT = 4    # parallel port S4 - pin 13

class fpga_jtag:

    def __init__(self, io):
        self.io = io
        self.io.wr_data(_FPGA_IE)

    def jtag_out(self, tck, tms, tdi = 0):
        """set the tck, tms and tdi bits"""
        val = _FPGA_IE
        if tck:
            val |= _FPGA_TCK
        if tms:
            val |= _FPGA_TMS
        if tdi:
            val |= _FPGA_TDI
        self.io.wr_data(val)

    def jtag_in(self):
        """get the tdo bit"""
        return (self.io.rd_status() >> _FPGA_TDO_BIT) & 1

    def test_reset(self, val):
        """control the test reset line"""
        # don't have a ~trst line
        pass

    def __str__(self):
        return '%s (xsa3s1000 fpga)' % str(self.io)

#-----------------------------------------------------------------------------

class board:

    def __init__(self, itf = None):
        # TODO - itf - interface selection
        self.pp = pport.io(0)

    def cpld_init(self):
        """setup the cpld access"""
        chain = jtag.jtag(bitbang.jtag_driver(cpld_jtag(self.pp)))
        chain.scan(jtag.IDCODE_XC9572XL)
        self.cpld = xc9500.xc9500(chain)

    def cpld_configure(self, filename):
        """configure the cpld with an svf file"""
        self.cpld.configure(''.join((_file_path, filename)))

    def fpga_init(self):
        """setup the fpga access"""
        chain = jtag.jtag(bitbang.jtag_driver(fpga_jtag(self.pp)))
        chain.scan(jtag.IDCODE_XC3S1000)
        print chain
#        self.fpga = xc9500.xc9500(chain)

    def __str__(self):
        return str(self.cpld)

#-----------------------------------------------------------------------------