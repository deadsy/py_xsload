# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
PyXS - Python based XSLoad tool for XESS FPGA Development Boards
"""
#------------------------------------------------------------------------------

import logging
import xsa3s1000

#------------------------------------------------------------------------------

def main():
    b = xsa3s1000.board()
    b.cpld_init()
    print b
    b.fpga_init()

    #print b
    #b.cpld_configure('p3jtag.svf')
    #b.cpld_configure('p4jtag.svf')
    #print '0x%08x' % b.cpld.rd_idcode()
    #print '0x%08x' % b.cpld.rd_usercode()





#------------------------------------------------------------------------------

logging.getLogger('').addHandler(logging.StreamHandler())
main()

#------------------------------------------------------------------------------