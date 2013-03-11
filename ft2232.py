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

import bits

#------------------------------------------------------------------------------

def to_bitsequence(x):
    """convert bits to a pyftdi bitsequence"""
    return BitSequence(value=x.val, length=x.n, msb = False)

def to_bits(x):
    val = 0
    for b in x.tobytes():
        val <<= 8
        val += b
    return bits.bits(len(x), val)

#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, vendor, product, interface):
        self.jtag = JtagEngine()
        self.jtag.configure(vendor, product, interface)

    def shift_data(self, tdi, tdo):
        """
        write (and possibly read) a bit stream from JTAG
        tdi - bit buffer of data to be written to the JTAG TDI pin
        tdo - bit buffer for the data read from the JTAG TDO pin (optional)
        """
        if tdo is None:
            pass
        else:
            pass
        # exit-x -> run-test/idle
        self.jtag.change_state('run_test_idle')

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        # run-test/idle -> shift-ir
        self.jtag.change_state('shift_ir')
        self.shift_data(tdi, tdo)

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        self.jtag.change_state('shift_dr')
        self.shift_data(tdi, tdo)

    def test_reset(self, val):
        """control the test reset line"""
        # TODO - pulse system reset line
        pass

    def state_reset(self):
        """goto the reset state"""
        self.jtag.change_state('test_logic_reset')

    def state_idle(self):
        """goto the idle state"""
        self.jtag.change_state('run_test_idle')

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain to the run-test/idle state"""
        self.jtag.reset()
        self.jtag.change_state('run_test_idle')

    def __str__(self):
        """return a string describing the device"""
        return 'ft2232'

#------------------------------------------------------------------------------

if __name__ == '__main__':

    x = bits.bits(val = 0x123412341234234234523453456346, n = 23)
    print x
    y = to_bitsequence(x)
    print y
    z = to_bits(y)
    print z
