# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
PyXS - Python based XSLoad tool for XESS FPGA Development Boards
"""
#------------------------------------------------------------------------------

import svf
import jtag_bitbang

#------------------------------------------------------------------------------

def main():
    x = svf.svf('dwnldpar.svf', jtag_bitbang.jtag(None))
    e = x.playback()
    if len(e):
        print '\n'.join(e)
    else:
        print 'no errors'

main()

#------------------------------------------------------------------------------