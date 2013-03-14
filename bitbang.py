# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Bit Bang JTAG Driver - JTAG via simple single bit IO lines
"""
#------------------------------------------------------------------------------

import time
import bits
import tap

#------------------------------------------------------------------------------

_TRST_TIME = 0.01

#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, io):
        self.io = io
        self.tap = tap.tap()
        self.state_reset()
        self.sir_end_state = 'IDLE'
        self.sdr_end_state = 'IDLE'

    def clock_tms(self, tms):
        """clock out a tms bit"""
        self.io.jtag_out(0, tms)
        self.io.jtag_out(1, tms)

    def clock_data_io(self, tms, tdi):
        """clock out tdi bit, sample tdo bit"""
        self.io.jtag_out(0, tms, tdi)
        self.io.jtag_out(1, tms, tdi)
        return self.io.jtag_in()

    def clock_data_o(self, tms, tdi):
        """clock out tdi bit"""
        self.io.jtag_out(0, tms, tdi)
        self.io.jtag_out(1, tms, tdi)

    def set_frequency(self, f):
        """set the tck frequency"""
        pass

    def state_x(self, dst):
        """change the TAP state from self.state to dst"""
        bits = self.tap.tms(self.state, dst)
        if not bits:
            # no state change
            assert self.state == dst
            return
        [self.clock_tms(b) for b in bits]
        self.state = dst

    def state_reset(self):
        """from *any* state go to the reset state"""
        self.state = '*'
        self.state_x('RESET')

    def shift_data(self, tdi, tdo):
        """
        write (and possibly read) a bit stream from JTAG
        tdi - bit buffer of data to be written to the JTAG TDI pin
        tdo - bit buffer for the data read from the JTAG TDO pin (optional)
        """
        if tdo is None:
            for i in range(tdi.n - 1):
                self.clock_data_o(0, tdi.shr())
            # last bit
            self.clock_data_o(1, tdi.shr())
        else:
            tdo.zeroes(tdi.n)
            for i in range(tdi.n - 1):
                tdo.shr(self.clock_data_io(0, tdi.shr()))
            # last bit
            tdo.shr(self.clock_data_io(1, tdi.shr()))
        # Note: we are now in the IR/DR EXIT1 state

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        self.state_x('IRSHIFT')
        self.shift_data(tdi, tdo)
        self.state = 'IREXIT1'
        self.state_x(self.sir_end_state)

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        self.state_x('DRSHIFT')
        self.shift_data(tdi, tdo)
        self.state = 'DREXIT1'
        self.state_x(self.sdr_end_state)

    def system_reset(self):
        """assert the ~SRST line to reset the target"""
        #TODO - pulse system reset line
        pass

    def test_reset(self, val):
        """control the test reset line"""
        self.io.test_reset(val)

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain"""
        self.test_reset(True)
        time.sleep(_TRST_TIME)
        self.test_reset(False)
        self.state_reset()

    def __str__(self):
        """return a string describing the device"""
        return 'bit bang using %s' % str(self.io)

#------------------------------------------------------------------------------
