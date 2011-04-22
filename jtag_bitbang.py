# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Bit Bang JTAG Driver - JTAG via simple single bit IO lines
"""
#------------------------------------------------------------------------------

class jtag:

    def __init__(self, io):
        self.io = io

    def set_frequency(self, f):
        """set the tck frequency"""
        pass

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        #_log.debug('jtagkey.scan_ir()')
        #self._shift_data(_rti2sir, tdi, tdo)
        pass

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        #_log.debug('jtagkey.scan_dr()')
        #self._shift_data(_rti2sdr, tdi, tdo)
        pass

    def reset_target(self):
        """assert the ~SRST line to reset the target"""
        #_log.debug('jtagkey.reset_target()')
        #self._flush()
        #self._write((ftdi.SET_BITS_HIGH, _JTAGKEY_GPIOH_DEFAULT_VALUE & ~_JTAGKEY_GPIOH_SRST, _JTAGKEY_GPIOH_DIRN), True)
        #time.sleep(_pause_20ms)
        #self._write((ftdi.SET_BITS_HIGH, _JTAGKEY_GPIOH_DEFAULT_VALUE, _JTAGKEY_GPIOH_DIRN), True)
        pass

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain to the run-test/idle state"""
        #_log.debug('jtagkey.reset_jtag()')
        #self._flush()
        #self._write((ftdi.SET_BITS_HIGH, _JTAGKEY_GPIOH_DEFAULT_VALUE & ~_JTAGKEY_GPIOH_TRST, _JTAGKEY_GPIOH_DIRN), True)
        #time.sleep(_pause_1ms)
        #self._write((ftdi.SET_BITS_HIGH, _JTAGKEY_GPIOH_DEFAULT_VALUE, _JTAGKEY_GPIOH_DIRN))
        ## some devices do not have trst connected - clock tms to ensure run-test/idle state
        #self._shift_tms(_2rti, True)
        pass

    def __str__(self):
        """return a string describing the device"""
        return 'bit bang jtag driver'

#------------------------------------------------------------------------------
