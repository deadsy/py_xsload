# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Definitions and functions specific to the Xilinx XC9500 CPLDs
"""
#------------------------------------------------------------------------------

import bits

#------------------------------------------------------------------------------
# IR/DR register lengths for XC9500

_IR_LEN = 8
_DR_IDCODE_LEN = 32
_DR_USERCODE_LEN = 32

#------------------------------------------------------------------------------
# IR opcodes for XC9500

_IR_USERCODE = 0xfd
_IR_IDCODE = 0xfe
_IR_BYPASS = 0xff

#------------------------------------------------------------------------------

class xc9500:
    """Xilinx XC9500 CPLD"""

    def __init__(self, chain, device):
        self.chain = chain
        self.device = device

    def wr_ir(self, val):
        """write instruction register"""
        wr = bits.bits(_IR_LEN, val)
        self.device.wr_ir(wr)

    def rd_dr(self, n):
        """read n bits from the current dr register"""
        wr = bits.bits(n)
        rd = bits.bits(n)
        self.device.rw_dr(wr, rd)
        return rd.scan((n,))[0]

    def rd_usercode(self):
        """read and return the jtag usercode"""
        self.wr_ir(_IR_USERCODE)
        return self.rd_dr(_DR_USERCODE_LEN)

    def rd_idcode(self):
        """read and return the jtag idcode"""
        self.wr_ir(_IR_IDCODE)
        return self.rd_dr(_DR_IDCODE_LEN)

    def __str__(self):
        return str(self.chain)

#------------------------------------------------------------------------------