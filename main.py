# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
PyXS - Python based XSLoad tool for XESS FPGA Development Boards
"""
#------------------------------------------------------------------------------

import jtag_bitbang
import jtag
import xsa3s1000
import pport

#------------------------------------------------------------------------------

def main1():
    x = svf.svf('dwnldpar.svf', jtag_bitbang.jtag(None))
    e = x.playback()
    if len(e):
        print '\n'.join(e)
    else:
        print 'no errors'


def main2():
    x = xsa3s1000.cpld(pport.io(0))
    x.jtag_out(1, 1, 1)
    while True:
        print x.jtag_in()

def main():
    driver = jtag_bitbang.jtag(xsa3s1000.cpld(pport.io(0)))
    chain = jtag.chain(0, driver)
    chain.scan()

main()

#------------------------------------------------------------------------------