# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
FT2232 JTAG Driver

This is a glue layer to provide a modified API to the pyftdi library.
https://github.com/eblot/pyftdi

"""
#-----------------------------------------------------------------------------

from pyftdi.pyftdi.jtag import JtagEngine
from pyftdi.pyftdi.bits import BitSequence

#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self):
        pass

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        pass

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        pass

    def test_reset(self, val):
        """control the test reset line"""
        pass

    def state_reset(self):
        """goto the reset state"""
        pass

    def state_idle(self):
        """goto the idle state"""
        pass

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain to the run-test/idle state"""
        self.state_idle()

    def __str__(self):
        """return a string describing the device"""
        return 'ft2232'

#------------------------------------------------------------------------------

if __name__ == '__main__':
    jtag = jtag_driver()

#------------------------------------------------------------------------------
