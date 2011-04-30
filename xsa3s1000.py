# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Definitions and functions specific to the XSA3S1000 board
See - http://www.xess.com/prods/prod035.php
"""
#-----------------------------------------------------------------------------

import time

import bitbang
import pport
import jtag
import xc9500
import spartan
import utils

#-----------------------------------------------------------------------------

class Error(Exception):
    pass

#-----------------------------------------------------------------------------
# cpld/fpga configuration files

_file_path = './bitfiles/XSA/3S1000/LPT/'

USERCODE_DOWNLOAD =  0x3c343e21
USERCODE_FCONFIG =  0x3c323e21
USERCODE_P3JTAG =  0x70336a74
USERCODE_P4JTAG =  0x70346a74

_cpld_files = {
    USERCODE_DOWNLOAD: 'dwnldpar.svf',
    USERCODE_FCONFIG: 'fcnfg.svf',
    USERCODE_P3JTAG: 'p3jtag.svf',
    USERCODE_P4JTAG: 'p4jtag.svf',
}

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
        return str(self.io)

#-----------------------------------------------------------------------------
# fpga parallel port to jtag interface (needs p3jtag.svf in the cpld)

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
        return str(self.io)

#-----------------------------------------------------------------------------
# fpga parallel port to select map interface (needs dwnldpar.svf in the cpld)
# The "select map" configuration scheme is the Xilinx term for an fpga getting
# configuration a byte at a time, clocked in by a host device.

_FPGA_CCLK  = (1 << 0)  # parallel port d0
_FPGA_PROGB = (1 << 7)  # parallel port d7
_NYBBLE_SHIFT = 2       # parallel port d5,d4,d3,d2 - nybble data

class fpga_smap:

    def __init__(self, io):
        self.io = io

    def start(self):
        """start the configuration process"""
        self.io.wr_data(0)
        self.io.wr_data(_FPGA_PROGB | _FPGA_CCLK)
        time.sleep(0.030)

    def wr(self, x):
        """clock a configuration byte to the fpga"""
        x = utils.reverse8(x)
        # upper nybble on falling edge of _FPGA_CCLK
        val = _FPGA_PROGB | _FPGA_CCLK | (((x & 0xf0) >> 4) << _NYBBLE_SHIFT)
        self.io.wr_data(val)
        val &= ~_FPGA_CCLK
        self.io.wr_data(val)
        # lower nybble on rising edge of _FPGA_CCLK
        val = _FPGA_PROGB | ((x & 0x0f) << _NYBBLE_SHIFT)
        self.io.wr_data(val)
        val |= _FPGA_CCLK
        self.io.wr_data(val)

    def finish(self):
        """finish the configuration process"""
        for i in range(8):
            self.io.wr_data(_FPGA_PROGB | _FPGA_CCLK)
            self.io.wr_data(_FPGA_PROGB)
        self.io.wr_data(_FPGA_PROGB | _FPGA_CCLK)

#-----------------------------------------------------------------------------

class board:

    def __init__(self, itf = None):
        # TODO - itf - interface selection
        self.pp = pport.io(0)
        # setup the cpld access
        chain = jtag.jtag(bitbang.jtag_driver(cpld_jtag(self.pp)))
        chain.scan(jtag.IDCODE_XC9572XL)
        self.cpld = xc9500.xc9500(chain)
        self.fpga = spartan.xc3s1000(fpga_smap(self.pp))

    def load_cpld(self, filename):
        """configure the cpld with an svf file"""
        self.cpld.configure(''.join((_file_path, filename)))

    def load_fpga(self, filename):
        """configure the fpga with a bit file"""
        # we need dwnldpar.svf in the cpld
        if self.cpld.rd_usercode() != USERCODE_DOWNLOAD:
            self.cpld.configure(''.join((_file_path, _cpld_files[USERCODE_DOWNLOAD])))
        self.fpga.configure(filename)

    #def fpga_init(self):
        #"""setup the fpga access"""
        #chain = jtag.jtag(bitbang.jtag_driver(fpga_jtag(self.pp)))
        #chain.scan(jtag.IDCODE_XC3S1000)
        #print chain

    def __str__(self):
        s = []
        s.append('XSA3S1000 Board')
        s.append(str(self.cpld))
        usercode = self.cpld.rd_usercode()
        s.append('usercode: 0x%08x (%s)' % (usercode, _cpld_files.get(usercode, '??')))
        return '\n'.join(s)

#-----------------------------------------------------------------------------