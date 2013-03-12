# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Definitions and functions specific to the Bus Blaster v2.5 board
See - http://www.seeedstudio.com/depot/bus-blaster-v2-jtag-debugger-p-807.html

The bus blaster has a ft2232h with a CPLD connected to it. By reprogramming the CPLD
you can adapt the board to an arbitrary pin out and a variety of voltage levels.

FT2232H to XC2C32A Connectivity

Channel A:
This channel is connected to the IO pins of the CPLD and is used for normal operations.

TCK    > AD0 > IO_31
TDI    > AD1 > IO_30
TDO    > AD2 > IO_29
TMS    > AD3 > IO_28
GPIOL0 > AD4 > IO_27
GPIOL1 > AD5 > IO_26
GPIOL2 > AD6 > IO_25
GPIOL3 > AD7 > IO_24
GPIOH0 > AC0 > IO_23
GPIOH1 > AC1 > IO_22
GPIOH2 > AC2 > IO_21
GPIOH3 > AC3 > IO_20
GPIOH4 > AC4 > IO_19
GPIOH5 > AC5 > IO_18
GPIOH6 > AC6 > IO_17
GPIOH7 > AC7 > IO_16

Channel B:
This channel is connected to the JTAG pins of the CPLD and is used for programming the CPLD.

TCK    > BD0 > TCK
TDI    > BD1 > TDI
TDO    > BD2 > TDO
TMS    > BD3 > TMS
GPIOL0..3 > Not connected
GPIOH0..7 > Not connected

"""
#-----------------------------------------------------------------------------

import jtag
import xc2c32a
import ft2232

#-----------------------------------------------------------------------------

_VID = 0x0403
_PID = 0x6010

_jtag_itf = 1 # external jtag is on the first interface
_cpld_itf = 2 # cpld jtag is on the second interface

#-----------------------------------------------------------------------------
# cpld configuration files

_cpld_files = {}

#-----------------------------------------------------------------------------

class board:

    def __init__(self, itf = None):
        # TODO - itf - interface selection
        # setup the cpld access
        chain = jtag.jtag(ft2232.jtag_driver(_VID, _PID, _cpld_itf))
        chain.scan(jtag.IDCODE_XC2C32A)
        self.cpld = xc2c32a.xc2c32a(chain)

    def load_cpld(self, filename):
        """configure the cpld with an svf file"""
        self.cpld.configure(''.join((_file_path, filename)))

    def __str__(self):
        s = []
        s.append('BusBlaster v2.5')
        s.append(str(self.cpld))
        usercode = self.cpld.rd_usercode()
        s.append('usercode: 0x%08x (%s)' % (usercode, _cpld_files.get(usercode, '?')))
        return '\n'.join(s)

#-----------------------------------------------------------------------------
