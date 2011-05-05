# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
JTAG Chain Controller
"""
#-----------------------------------------------------------------------------

import bits

#-----------------------------------------------------------------------------

class Error(Exception):
    pass

#-----------------------------------------------------------------------------

_max_devices = 4
_flush_size = _max_devices * 32
_idcode_length = 32

#-----------------------------------------------------------------------------
# Device ID Codes and Lookup Table

IDCODE_XC9572XL = 0x09604093
IDCODE_XC3S1000 = 0x01428093
IDCODE_XC3S200A = 0x02218093

device_table = (
    (IDCODE_XC9572XL, 'Xilinx XC9572XL CPLD', 8, 0xfffffff),
    (IDCODE_XC3S1000, 'Xilinx XC3S1000 FPGA', 6, 0xfffffff),
    (IDCODE_XC3S200A, 'Xilinx XC3S200A FPGA', 6, 0xfffffff),
)


def lookup_device(x):
    """lookup a device by idcode"""
    for (idcode, name, irlen, mask) in device_table:
        if x & mask == idcode:
            return (name, irlen, mask)
    return ('unknown', 0, 0xffffffff)

#-----------------------------------------------------------------------------

class jtag:

    def __init__(self, driver):
        self.driver = driver

    def scan(self, idcode_x):
        """try to find the device with idcode on the jtag chain"""
        self.driver.reset_jtag()
        self.ndevs = self.num_devices()
        self.irlen_total = self.ir_length()
        self.idcode = 0
        self.ndevs_before = 0
        self.ndevs_after = 0
        self.irlen_before = 0
        self.irlen_after = 0
        found = False
        for idcode in self.reset_idcodes():
            (name, irlen, mask) = lookup_device(idcode)
            if name == 'unknown':
                raise Error, 'unknown device on jtag chain - idcode 0x%08x' % idcode
            if idcode_x == idcode & mask:
                found = True
                self.irlen = irlen
                self.idcode = idcode
                self.name = name
                continue
            if not found:
                self.irlen_before += irlen
                self.ndevs_before += 1
            else:
                self.irlen_after += irlen
                self.ndevs_after += 1
        if self.idcode == 0:
            raise Error, 'unable to find device on jtag chain - idcode 0x%08x' % self.idcode
        if (self.irlen_before + self.irlen + self.irlen_after) != self.irlen_total:
            raise Error, 'incorrect ir lengths - %d + (%d) + %d != %d' % (self.irlen_before, self.irlen, self.irlen_after, self.irlen_total)

    def num_devices(self):
        """return the number of JTAG devices in the chain"""
        # put every device into bypass mode (IR = all 1's)
        tdi = bits.bits()
        tdi.ones(_flush_size)
        self.driver.scan_ir(tdi)
        # now each DR is a single bit
        # the DR chain length is the number of devices
        return self.dr_length()

    def chain_length(self, scan):
        """return the length of the JTAG chain"""
        tdo = bits.bits()
        # build a 000...001000...000 flush buffer for tdi
        tdi = bits.bits(_flush_size)
        tdi.append_ones(1)
        tdi.append_zeroes(_flush_size)
        scan(tdi, tdo)
        # the first bits are junk
        tdo.drop_lsb(_flush_size)
        # work out how many bits tdo is behind tdi
        s = tdo.bit_str()
        s = s.lstrip('0')
        if len(s.replace('0', '')) != 1:
            raise Error, 'unexpected result from jtag chain - multiple 1\'s'
        return len(s) - 1

    def dr_length(self):
        """
        return the length of the DR chain
        note: DR chain length is a function of current IR chain state
        """
        return self.chain_length(self.driver.scan_dr)

    def ir_length(self):
        """return the length of the ir chain"""
        return self.chain_length(self.driver.scan_ir)

    def reset_idcodes(self):
        """return a tuple of the idcodes for the JTAG chain"""
        # a JTAG reset leaves DR as the 32 bit idcode for each device.
        self.driver.reset_jtag()
        tdi = bits.bits(self.ndevs * _idcode_length)
        tdo = bits.bits()
        self.driver.scan_dr(tdi, tdo)
        return tdo.scan((_idcode_length, ) * self.ndevs)

    def wr_ir(self, wr):
        """
        write to IR for a device
        wr: the bitbuffer to be written to ir for this device
        note - other devices will be placed in bypass mode (ir = all 1's)
        """
        tdi = bits.bits()
        tdi.append_ones(self.irlen_before)
        tdi.append(wr)
        tdi.append_ones(self.irlen_after)
        self.driver.scan_ir(tdi)

    def rw_ir(self, wr, rd):
        """
        read/write IR for a device
        wr: bitbuffer to be written to ir for this device
        rd: bitbuffer to be read from ir for this device
        note - other devices are assumed to be in bypass mode
        """
        tdi = bits.bits()
        tdi.append_ones(self.irlen_before)
        tdi.append(wr)
        tdi.append_ones(self.irlen_after)
        self.driver.scan_ir(tdi, rd)
        # strip the ir bits from the bypassed devices
        rd.drop_msb(self.irlen_before)
        rd.drop_lsb(self.irlen_after)

    def wr_dr(self, wr):
        """
        write to DR for a device
        wr: bitbuffer to be written to dr for this device
        note - other devices are assumed to be in bypass mode
        """
        tdi = bits.bits()
        tdi.append_ones(self.ndevs_before)
        tdi.append(wr)
        tdi.append_ones(self.ndevs_after)
        self.driver.scan_dr(tdi)

    def rw_dr(self, wr, rd):
        """
        read/write DR for a device
        wr: bitbuffer to be written to dr for this device
        rd: bitbuffer to be read from dr for this device
        note - other devices are assumed to be in bypass mode
        """
        tdi = bits.bits()
        tdi.append_ones(self.ndevs_before)
        tdi.append(wr)
        tdi.append_ones(self.ndevs_after)
        self.driver.scan_dr(tdi, rd)
        # strip the dr bits from the bypassed devices
        rd.drop_msb(self.ndevs_before)
        rd.drop_lsb(self.ndevs_after)

    def __str__(self):
        """return a string describing the jtag chain"""
        s = []
        s.append('jtag: %s' % self.driver)
        s.append('device: idcode 0x%08x ir length %d bits - %s' % (self.idcode, self.irlen, self.name))
        if self.ndevs > 1:
            s.append('chain: %d devices, %d before %d after' % (self.ndevs, self.ndevs_before, self.ndevs_after))
            s.append('chain: %d ir bits total, %d before %d after' % (self.irlen_total, self.irlen_before, self.irlen_after))
        return '\n'.join(s)

#-----------------------------------------------------------------------------
