# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Definitions and functions specific to the XuLA board
See - http://www.xess.com/prods/prod048.php
"""
#-----------------------------------------------------------------------------

import jtag
import xsusb
import utils

#-----------------------------------------------------------------------------

class Error(Exception):
    pass

#-----------------------------------------------------------------------------

class board:

    def __init__(self, itf = None):
        # TODO - itf - interface selection
        # setup the fpga access
        self.xsusb = xsusb.xsusb(0)
        self.get_info()

        chain = jtag.jtag(xsusb.jtag_driver(self.xsusb))
        chain.scan(0)


    def get_info(self):
        """get the product information from the usb interface"""
        info = self.xsusb.info

        print info
        if sum(info) & 0xff != 0:
            raise Error, 'bad checksum on usb device information'
        # grab the information fields
        self.pid = '0x%02x%02x' % info[1:3]
        self.version = '%d.%d' % info[3:5]
        # the product name is a null terminated string
        name = info[5:]
        name = name[:name.index(0)]
        self.name = utils.b2s(name) 

        print self.pid
        print self.version
        print self.name









    def __str__(self):
        s = []
        s.append('XuLA Board')
        return '\n'.join(s)

#-----------------------------------------------------------------------------
