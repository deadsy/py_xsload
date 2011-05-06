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
import spartan

#-----------------------------------------------------------------------------

class Error(Exception):
    pass

#-----------------------------------------------------------------------------

class board:

    def __init__(self, itf = None):
        # TODO - itf - interface selection
        self.dev = xsusb.usb_dev(0)
        self.ep1 = xsusb.usb_ep(self.dev, 1)

        # get the device information
        info = self.ep1.get_device_info()
        # validate the response and extract fields
        if sum(info) & 0xff != 0:
            raise Error, 'bad checksum on device information'
        # the product name is a null terminated string
        name = info[5:]
        name = name[:name.index(0)]
        self.name = utils.b2s(name) 
        if self.name != 'XuLA':
            raise Error, 'invalid product name: is "%s" expected "XuLA"' % self.name
        # grab the information fields
        self.pid = (info[1] << 8) | info[2]
        self.version = '%d.%d' % info[3:5]

        # setup the jtag interface
        chain = jtag.jtag(xsusb.jtag_driver(self.ep1))
        chain.scan(jtag.IDCODE_XC3S200A)
        self.fpga = spartan.xc3s200a(chain)

    def __str__(self):
        s = []
        s.append('%s version %s/%d' % (self.name, self.version, self.pid))
        s.append(str(self.fpga))
        return '\n'.join(s)

#-----------------------------------------------------------------------------
