# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
FT2232 Based JTAG Driver

Note:
This code uses ftdi.py and usbtools.py both taken from the pyftdi project.
The pyftdi project has some JTAG functions but the JTAG api and their
method for storing bit streams is different from the rest of this code,
so I've only borrowed the ftdi specific portions.
"""
#-----------------------------------------------------------------------------

import time
import array
from ftdi import Ftdi

#------------------------------------------------------------------------------

_TRST_TIME = 0.01

#------------------------------------------------------------------------------

_GPIO_TCK = (1 << 0) # output, normally low
_GPIO_TDI = (1 << 1) # output, sampled on rising edge of tck
_GPIO_TDO = (1 << 2) # input
_GPIO_TMS = (1 << 3) # output, sampled on rising edge of tck

#-----------------------------------------------------------------------------
# tms bit sequences

def _tms_bits(bits):
    """convert a left to right bit string to an mpsee (len, bits) tuple"""
    l = list(bits)
    # tms is shifted lsb first
    l.reverse()
    # only bits 0 thru 6 are shifted on tms - tdi is set to bit 7 (and is left there)
    # len = n means clock out n + 1 bits
    return (len(bits) - 1, int(''.join(l), 2) & 127)

# pre-canned jtag state machine transitions
_x2rti = _tms_bits('111110')  # any state -> run-test/idle
_x2r = _tms_bits('11111')  # any state -> reset
_rti2sir = _tms_bits('1100') # run-test/idle -> shift-ir
_rti2sdr = _tms_bits('100')  # run-test/idle -> shift-dr
_sx2rti = _tms_bits('110')   # shift-x -> run-test/idle

#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, vid, pid, itf):
        self.ftdi = Ftdi()
        self.ftdi.open_mpsse(vid, pid, itf)
        self.wrbuf = array.array('B')

    def __del__(self):
        self.ftdi.close()

    def flush(self):
        """flush the write buffer to the ft2232"""
        if len(self.wrbuf) > 0:
            self.ftdi.write_data(self.wrbuf)
            del self.wrbuf[0:]

    def write(self, buf, flush = False):
        """queue write data to send to ft2232"""
        self.wrbuf.extend(buf)
        if flush:
            self.flush()

    def shift_tms(self, tms, flush = False):
        self.write((Ftdi.WRITE_BITS_TMS_NVE, tms[0], tms[1]), flush)

    def shift_data(self, tdi, tdo):
        assert False

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        # run-test/idle -> shift-ir
        self.shift_tms(_rti2sir)
        self.shift_data(tdi, tdo)

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        # run-test/idle -> shift-dr
        self.shift_tms(_rti2sdr)
        self.shift_data(tdi, tdo)

    def system_reset(self):
        """assert the ~SRST line to reset the target"""
        #TODO - pulse system reset line
        pass

    def test_reset(self, val):
        """control the test reset line"""
        #TODO - control the test reset line
        pass

    def state_reset(self):
        """goto the reset state"""
        # any state -> reset
        self.shift_tms(_x2r, True)

    def state_idle(self):
        """goto the idle state"""
        # any state -> run-test/idle
        self.shift_tms(_x2rti, True)

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain to the run-test/idle state"""
        self.test_reset(True)
        time.sleep(_TRST_TIME)
        self.test_reset(False)
        self.state_idle()

    def __str__(self):
        """return a string describing the device"""
        return 'ft2232'

#------------------------------------------------------------------------------
