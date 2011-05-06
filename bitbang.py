# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Bit Bang JTAG Driver - JTAG via simple single bit IO lines
"""
#------------------------------------------------------------------------------

import logging
import time

import bits

#------------------------------------------------------------------------------

_log = logging.getLogger('bitbang')
#_log.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------

_TRST_TIME = 0.01

#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, io):
        self.io = io

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
        # exit-x -> run-test/idle
        [self.clock_tms(x) for x in (1,0)]

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        _log.debug('jtag.scan_ir()')
        # run-test/idle -> shift-ir
        [self.clock_tms(x) for x in (1,1,0,0)]
        self.shift_data(tdi, tdo)

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        _log.debug('jtag.scan_dr()')
        # run-test/idle -> shift-dr
        [self.clock_tms(x) for x in (1,0,0)]
        self.shift_data(tdi, tdo)

    def system_reset(self):
        """assert the ~SRST line to reset the target"""
        _log.debug('jtag.system_reset()')
        #TODO - pulse system reset line
        pass

    def test_reset(self, val):
        """control the test reset line"""
        _log.debug('jtag.test_reset()')
        self.io.test_reset(val)

    def state_reset(self):
        """goto the reset state"""
        # any state -> reset
        [self.clock_tms(x) for x in (1,1,1,1,1)]

    def state_idle(self):
        """goto the idle state"""
        # any state -> run-test/idle
        [self.clock_tms(x) for x in (1,1,1,1,1,0)]

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain to the run-test/idle state"""
        _log.debug('jtag.reset_jtag()')
        self.test_reset(True)
        time.sleep(_TRST_TIME)
        self.test_reset(False)
        self.state_idle()

    def __str__(self):
        """return a string describing the device"""
        return 'bit bang using %s' % str(self.io)

#------------------------------------------------------------------------------
