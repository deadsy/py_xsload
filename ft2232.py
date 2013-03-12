# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
FT2232 Based JTAG Driver

Note:
This code uses ftdi.py and usbtools.py both taken from the pyftdi project.
The pyftdi project has some JTAG functions but the JTAG api and their
method for storing bit streams is different from the rest of this code,
so I've only borrowed the ftdi specific portions.
"""
#-----------------------------------------------------------------------------

import time
import array
import sys
from ftdi import Ftdi

#------------------------------------------------------------------------------

_READ_RETRIES = 4

#------------------------------------------------------------------------------
# JTAG/GPIO Lines in MPSSE Mode

_TCK    = (1 << 0) # output, normally low
_TDI    = (1 << 1) # output, sampled on rising edge of tck
_TDO    = (1 << 2) # input
_TMS    = (1 << 3) # output, sampled on rising edge of tck
_GPIOL0 = (1 << 4)
_GPIOL1 = (1 << 5)
_GPIOL2 = (1 << 6)
_GPIOL3 = (1 << 7)
_GPIOH0 = (1 << 8)
_GPIOH1 = (1 << 9)
_GPIOH2 = (1 << 10)
_GPIOH3 = (1 << 11)
_GPIOH4 = (1 << 12)
_GPIOH5 = (1 << 13)
_GPIOH6 = (1 << 14)
_GPIOH7 = (1 << 15)

# Commands in MPSSE Mode
_MPSSE_WRITE_NEG = 0x01   # Write TDI/DO on negative TCK/SK edge
_MPSSE_BITMODE   = 0x02   # Write bits, not bytes
_MPSSE_READ_NEG  = 0x04   # Sample TDO/DI on negative TCK/SK edge
_MPSSE_LSB       = 0x08   # LSB first
_MPSSE_DO_WRITE  = 0x10   # Write TDI/DO
_MPSSE_DO_READ   = 0x20   # Read TDO/DI
_MPSSE_WRITE_TMS = 0x40   # Write TMS/CS

#-----------------------------------------------------------------------------
# MSB/LSB for 16 bit values

def _msb(val): return (val >> 8) & 255
def _lsb(val): return val & 255

#-----------------------------------------------------------------------------
# tms bit sequences

def _tms_bits(bits):
    """convert a left to right bit string to an mpsee (len, bits) tuple"""
    l = list(bits)
    # tms is shifted lsb first
    l.reverse()
    # only bits 0 thru 6 are shifted on tms - tdi is set to bit 7 (and is left there)
    # len = n means clock out n + 1 bits
    return (len(bits) - 1, int(''.join(l), 2) & 127)

# pre-canned jtag state machine transitions
_x2rti = _tms_bits('111110')  # any state -> run-test/idle
_x2r = _tms_bits('11111')  # any state -> reset
_rti2sir = _tms_bits('1100') # run-test/idle -> shift-ir
_rti2sdr = _tms_bits('100')  # run-test/idle -> shift-dr
_sx2rti = _tms_bits('110')   # shift-x -> run-test/idle

#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, vendor, product, interface):
        self.ftdi = Ftdi()
        try:
            self.ftdi.open_mpsse(vendor, product, interface)
        except IOError as e:
            print "ft2232 jtag driver: %s" % str(e)
            self.ftdi = None
            sys.exit(0)
        self.wrbuf = array.array('B')
        # setup the gpio lines
        self.gpio_dir = _TCK | _TDI | _TMS
        self.gpio_val = 0
        self.ftdi.write_data((Ftdi.SET_BITS_LOW, _lsb(self.gpio_val), _lsb(self.gpio_dir)))
        self.ftdi.write_data((Ftdi.SET_BITS_HIGH, _msb(self.gpio_val), _msb(self.gpio_dir)))

    def reset_jtag(self):
        # TODO - pulse test reset line if we have one
        self.state_idle()

    def __del__(self):
        if self.ftdi:
            self.ftdi.close()

    def gpio_out(self, gpio):
        if gpio <= _GPIOL3:
            self.ftdi.write_data((Ftdi.SET_BITS_LOW, _lsb(self.gpio_val), _lsb(self.gpio_dir)))
        else:
            self.ftdi.write_data((Ftdi.SET_BITS_HIGH, _msb(self.gpio_val), _msb(self.gpio_dir)))

    def gpio_set(self, gpio):
        """set a gpio pin"""
        self.gpio_dir |= gpio
        self.gpio_val |= gpio
        self.gpio_out(gpio)

    def gpio_clr(self, gpio):
        """clear a gpio pin"""
        self.gpio_dir |= gpio
        self.gpio_val &= ~gpio
        self.gpio_out(gpio)

    def gpio_rd(self, gpio):
        """read a gpio pin"""
        if gpio <= _GPIOL3:
            self.ftdi.write_data((Ftdi.GET_BITS_LOW,))
            val = self.ftdi.read_data_bytes(1, _READ_RETRIES)[0]
        else:
            self.ftdi.write_data((Ftdi.GET_BITS_HIGH,))
            val = self.ftdi.read_data_bytes(1, _READ_RETRIES)[0]
            val <<= 8
        return (val & gpio) != 0

    def flush(self):
        """flush the write buffer to the ft2232"""
        if len(self.wrbuf) > 0:
            self.ftdi.write_data(self.wrbuf)
            del self.wrbuf[0:]

    def write(self, buf, flush = False):
        """queue write data to send to ft2232"""
        self.wrbuf.extend(buf)
        if flush:
            self.flush()

    def shift_tms(self, tms, flush = False):
        cmd = _MPSSE_WRITE_TMS | _MPSSE_BITMODE | _MPSSE_LSB | _MPSSE_WRITE_NEG
        self.write((cmd, tms[0], tms[1]), flush)

    def shift_data(self, tdi, tdo):
        """
        write (and possibly read) a bit stream from the JTAGkey
        tdi - bit buffer of data to be written to the JTAG TDI pin
        tdo - bit buffer for the data read from the JTAG TDO pin (optional)
        """
        wr = tdi.get()
        io_bits = tdi.n - 1
        io_bytes = io_bits >> 3
        io_bits &= 0x07
        last_bit = (wr[io_bytes] << (7 - io_bits)) & 128

        if tdo is not None:
            read_cmd = _MPSSE_DO_READ
            read_len = io_bytes + 1
            if io_bits:
                read_len += 1
        else:
            read_cmd = 0
            read_len = 0

        # write out the full bytes
        if io_bytes:
            cmd = read_cmd | _MPSSE_DO_WRITE | _MPSSE_LSB | _MPSSE_WRITE_NEG
            num = io_bytes - 1
            self.write((cmd, _lsb(num), _msb(num)))
            self.write(wr[0:io_bytes])

        # write out the remaining bits
        if io_bits:
            cmd = read_cmd | _MPSSE_DO_WRITE | _MPSSE_LSB | _MPSSE_BITMODE | _MPSSE_WRITE_NEG
            self.write((cmd, io_bits - 1, wr[io_bytes]))

        # the last bit of output data is bit 7 of the tms value (goes onto tdi)
        # continue to read during the return to run-test/idle to get the last bit of tdo data
        cmd = read_cmd | _MPSSE_WRITE_TMS | _MPSSE_BITMODE | _MPSSE_LSB | _MPSSE_WRITE_NEG
        self.write((cmd, _sx2rti[0], _sx2rti[1] | last_bit))

        # if we are only writing, return
        if tdo is None:
            self.flush()
            return

        # make the ft2232 flush its data back to the PC
        self.write((Ftdi.SEND_IMMEDIATE,), True)
        rd = self.ftdi.read_data_bytes(read_len, _READ_RETRIES)

        if io_bits:
            # the n partial bits are in the top n bits of the byte
            # move them down to the bottom
            rd[-2] >>= (8 - io_bits)

        # get the last bit from the tms response byte (last byte)
        last_bit = (rd[-1] >> (7 - _sx2rti[0])) & 1
        last_bit <<= io_bits

        # add the last bit
        if io_bits:
            # drop the tms response byte
            del rd[-1]
            # or it onto the io_bits byte
            rd[-1] |= last_bit
        else:
            # replace the tms response byte
            rd[-1] = last_bit

        # copy to the bit buffer
        tdo.set(tdi.n, rd)

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        # run-test/idle -> shift-ir
        self.shift_tms(_rti2sir)
        self.shift_data(tdi, tdo)

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        # run-test/idle -> shift-dr
        self.shift_tms(_rti2sdr)
        self.shift_data(tdi, tdo)

    def state_reset(self):
        """goto the reset state"""
        # any state -> reset
        self.shift_tms(_x2r, True)

    def state_idle(self):
        """goto the idle state"""
        # any state -> run-test/idle
        self.shift_tms(_x2rti, True)

    def __str__(self):
        """return a string describing the device"""
        return self.ftdi.type

#------------------------------------------------------------------------------
