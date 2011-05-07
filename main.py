# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
PyXS - Python based XSLoad tool for XESS FPGA Development Boards
"""
#------------------------------------------------------------------------------

import logging

import xsa3s1000
import xula
import bitfile

#------------------------------------------------------------------------------

def main3():
    bitfile.decode('xessdemo.bit')

def main2():
    b = xsa3s1000.board2()
    print b

def main1():
    b = xsa3s1000.board()
    print b
    b.load_fpga('xessdemo.bit')

def main():
    b = xula.board()
    print b

#------------------------------------------------------------------------------

logging.getLogger('').addHandler(logging.StreamHandler())
main3()

#------------------------------------------------------------------------------