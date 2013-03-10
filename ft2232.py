# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
FT2232 JTAG Driver - JTAG using the FT2232 USB/Serial Chip
"""
#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, io):
        self.io = io

    def clock_tms(self, bits):
        n = bits[0]
        cmd = [_CMD_TAP_SEQ, n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff, (n >> 24) & 0xff]
        cmd.extend([_PUT_TDI_MASK | _PUT_TMS_MASK, bits[1], 0])
        self.io.txrx(utils.b2s(cmd))

    def shift_data(self, tdi, tdo):
        """
        write (and possibly read) a bit stream from JTAG
        tdi - bit buffer of data to be written to the JTAG TDI pin
        tdo - bit buffer for the data read from the JTAG TDO pin (optional)
        """
        n = len(tdi)
        cmd = [0, n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff, (n >> 24) & 0xff]
        if (tdi.val != 0) and (tdo is None):
            cmd[0] = _CMD_TDI
            self.io.txrx(utils.b2s(cmd))
            self.io.txrx(utils.b2s(tdi.get()))
        elif (tdi.val == 0) and (tdo is not None):
            cmd[0] = _CMD_TDO
            self.io.txrx(utils.b2s(cmd))
            rx = self.io.txrx(None, (n + 7)/8)
            tdo.set(n, rx)
        elif (tdi.val != 0) and (tdo is not None):
            cmd[0] = _CMD_TDI_TDO
            self.io.txrx(utils.b2s(cmd))
            rx = self.io.txrx(utils.b2s(tdi.get()), (n + 7)/8)
            tdo.set(n, rx)
        # exit-x -> run-test/idle
        self.clock_tms(_ex2rti)

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        ## run-test/idle -> shift-ir
        self.clock_tms(_rti2sir)
        self.shift_data(tdi, tdo)

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        ## run-test/idle -> shift-dr
        self.clock_tms(_rti2sdr)
        self.shift_data(tdi, tdo)

    def test_reset(self, val):
        """control the test reset line"""
        pass

    def state_reset(self):
        """goto the reset state"""
        # any state -> reset
        self.clock_tms(_2reset)

    def state_idle(self):
        """goto the idle state"""
        # any state -> run-test/idle
        self.clock_tms(_2rti)

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain to the run-test/idle state"""
        self.state_idle()

    def __str__(self):
        """return a string describing the device"""
        return 'ft2232'

#------------------------------------------------------------------------------
