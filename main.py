# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
PyXS - Python based XSLoad tool for XESS FPGA Development Boards
"""
#------------------------------------------------------------------------------

import logging

import xsa3s1000
import xula
import busblaster
import bitfile

#------------------------------------------------------------------------------

def main5():
    b = busblaster.board()
    print b

def main4():
    b = xula.board()
    print b

def main3():
    bitfile.decode('xessdemo.bit')

def main2():
    b = xsa3s1000.board2()
    print b

def main1():
    b = xsa3s1000.board()
    print b
    b.load_fpga('/home/jasonh/work/fpga/jasonh/j1_test/src/firmware/j1_test.bit')
    #b.load_fpga('/home/jasonh/work/fpga/jasonh/ram_test/src/rt.bit')
    #b.load_fpga('/home/jasonh/work/fpga/jasonh/j1_demo/src/j1demo.bit')
    #b.load_fpga('/home/jasonh/work/fpga/jasonh/uart_test/uart_test.bit')
    #b.load_fpga('/home/jasonh/work/fpga/jasonh/db_test/db_test.bit')

#------------------------------------------------------------------------------

logging.getLogger('').addHandler(logging.StreamHandler())
main5()

#------------------------------------------------------------------------------
