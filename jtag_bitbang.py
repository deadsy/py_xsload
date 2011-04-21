# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Bit Bang JTAG Driver - JTAG via simple single bit IO lines
"""
#------------------------------------------------------------------------------

class jtag:

    def __init__(self, io):
        self.io = io

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        print('scan_ir tdi %s tdo %s' % (tdi, tdo))

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        print('scan_dr tdi %s tdo %s' % (tdi, tdo))

    def set_frequency(self, f):
        """set the tck frequency"""
        pass

    def delay(self, n):
        """delay n tck cycles"""
        print 'delay %d tck cycles' % n

#------------------------------------------------------------------------------
