# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Definitions and functions specific to the Bus Blaster v2.5 board
See - http://www.seeedstudio.com/depot/bus-blaster-v2-jtag-debugger-p-807.html
"""
#-----------------------------------------------------------------------------

import jtag
import xc2c32a
import ft2232

#-----------------------------------------------------------------------------
# cpld configuration files

_cpld_files = {}

#-----------------------------------------------------------------------------

class board:

    def __init__(self, itf = None):
        # TODO - itf - interface selection
        # setup the cpld access
        chain = jtag.jtag(ft2232.jtag_driver())
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
        s.append('usercode: 0x%08x (%s)' % (usercode, _cpld_files.get(usercode, '??')))
        return '\n'.join(s)

#-----------------------------------------------------------------------------
