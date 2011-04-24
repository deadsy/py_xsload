# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
JTAG Chain Controller
"""
#-----------------------------------------------------------------------------

import array
import bits

#-----------------------------------------------------------------------------

class Error(Exception):
    pass

#-----------------------------------------------------------------------------

_max_devices = 32
_flush_size = _max_devices * 32
_idcode_length = 32

#-----------------------------------------------------------------------------
# Device ID Codes and Lookup Table

IDCODE_XC9572XL = 0x09604093

device_table = (
    (IDCODE_XC9572XL, 'Xilinx XC9572XL CPLD', 8, 0xfffffff),
)

def lookup_device(x):
    """lookup a device by idcode"""
    for (idcode, name, irlen, mask) in device_table:
        if x & mask == idcode:
            return (name, irlen)
    return ('Unknown', 0)

#-----------------------------------------------------------------------------

class device:
    """JTAG Device"""
    def __init__(self, jtag, idx, idcode, name, irlen):
        self.jtag = jtag
        self.idx = idx
        self.idcode = idcode
        self.name = name
        self.irlen = irlen

    def wr_ir(self, wr):
        self.jtag.wr_ir(self, wr)

    def rw_dr(self, wr, rd):
        self.jtag.rw_dr(self, wr, rd)

    def wr_dr(self, wr):
        self.jtag.wr_dr(self, wr)

    def __str__(self):
        return 'device %d: idcode 0x%08x irlen %d bits - %s' % (self.idx, self.idcode, self.irlen, self.name)

#-----------------------------------------------------------------------------

class chain:
    """JTAG Chain Controller"""
    def __init__(self, idx, driver):
        self.idx = idx
        self.driver = driver
        self.devices = []

    def scan(self):
        """examine the JTAG chain and identify what we have"""
        self.driver.reset_jtag()
        self.ndevs = self.num_devices()
        self.irlen = self.ir_length()
        unknown = []
        for idcode in self.reset_idcodes():
            (name, irlen) = lookup_device(idcode)
            dev = device(self, len(self.devices), idcode, name, irlen)
            self.devices.append(dev)
            if name == 'Unknown':
                unknown.append(dev)
        # assume that a single unknown device makes up any irlen shortfall
        delta = self.irlen - self.device_ir_length()
        if (delta > 0) and (len(unknown) == 1):
            unknown[0].irlen = delta

    def reset_target(self):
        """reset the target system"""
        self.driver.reset_target()

    def reset_jtag(self):
        """set all JTAG devices in the chain to the run-test/idle state"""
        self.driver.reset_jtag()

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

    def device_ir_length(self):
        """return the summed ir length of the devices on the chain"""
        irlen = 0
        for device in self.devices:
            irlen += device.irlen
        return irlen

    def num_devices(self):
        """return the number of JTAG devices in the chain"""
        # put every device into bypass mode (IR = all 1's)
        tdi = bits.bits()
        tdi.ones(_flush_size)
        self.driver.scan_ir(tdi)
        # now each DR is a single bit
        # the DR chain length is the number of devices
        return self.dr_length()

    def reset_idcodes(self):
        """return a tuple of the idcodes for the JTAG chain"""
        # a JTAG reset leaves DR as the 32 bit idcode for each device.
        self.driver.reset_jtag()
        tdi = bits.bits(self.ndevs * _idcode_length)
        tdo = bits.bits()
        self.driver.scan_dr(tdi, tdo)
        return tdo.scan((_idcode_length, ) * self.ndevs)

    def wr_ir(self, dev, wr):
        """
        write to IR for a device
        dev: the device that needs ir written
        wr: the bitbuffer to be written to ir for this device
        note - other devices will be placed in bypass mode (ir = all 1's)
        """
        tdi = bits.bits()
        for device in self.devices:
            if dev == device:
                tdi.append(wr)
            else:
                tdi.append_ones(device.irlen)
        self.driver.scan_ir(tdi)

    def wr_dr(self, dev, wr):
        """
        write to DR for a device
        dev: the device that needs dr written
        wr: bitbuffer to be written to dr for this device
        note - other devices are assumed to be in bypass mode
        """
        tdi = bits.bits()
        for device in self.devices:
            if dev == device:
                tdi.append(wr)
            else:
                tdi.append_ones(1)
        self.driver.scan_dr(tdi)

    def rw_dr(self, dev, wr, rd):
        """
        read/write DR for a device
        dev: the device that needs dr read/written
        wr: bitbuffer to be written to dr for this device
        rd: bitbuffer to be read from dr for this device
        note - other devices are assumed to be in bypass mode
        """
        tdi = bits.bits()
        before = 0
        after = 0
        found = False
        for device in self.devices:
            if dev == device:
                tdi.append(wr)
                found = True
            else:
                tdi.append_ones(1)
                if not found:
                    before += 1
                else:
                    after += 1
        self.driver.scan_dr(tdi, rd)
        # strip the dr bits from the bypassed devices
        rd.drop_msb(before)
        rd.drop_lsb(after)

    def __str__(self):
        """return a string describing the jtag chain"""
        err_str = ''
        title_str = 'JTAG chain %d\n' % self.idx
        ir_str = 'chain IR length: %d bits\n' % self.irlen
        drv_str = 'driver: %s\n' % self.driver
        if len(self.devices) ==0:
            dev_str = 'no devices\n'
        else:
            dev_str = '\n'.join([str(device) for device in self.devices])
            if self.device_ir_length() != self.irlen:
                err_str = '\nassumed/actual IR length mismatch: %d/%d bits' % (self.device_ir_length(), self.irlen)
        return ''.join([title_str, drv_str, ir_str, dev_str, err_str])

#-----------------------------------------------------------------------------
