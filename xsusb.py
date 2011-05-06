# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
XSUSB JTAG Driver - JTAG via USB and a Microcontroller
"""
#------------------------------------------------------------------------------

import logging
import usb
import time

import utils

#------------------------------------------------------------------------------

class Error(Exception):
    pass

#------------------------------------------------------------------------------
# command set

_CMD_READ_VERSION       = 0x00 # Read the product version information.
_CMD_READ_FLASH         = 0x01 # Read from the device flash.
_CMD_WRITE_FLASH        = 0x02 # Write to the device flash.
_CMD_ERASE_FLASH        = 0x03 # Erase the device flash.
_CMD_READ_EEDATA        = 0x04 # Read from the device EEPROM.
_CMD_WRITE_EEDATA       = 0x05 # Write to the device EEPROM.
_CMD_READ_CONFIG        = 0x06 # Read from the device configuration memory.
_CMD_WRITE_CONFIG       = 0x07 # Write to the device configuration memory.
_CMD_ID_BOARD           = 0x31 # Flash the device LED to identify which device is being communicated with.
_CMD_UPDATE_LED         = 0x32 # Change the state of the device LED.
_CMD_INFO               = 0x40 # Get information about the USB interface.
_CMD_SENSE_INVERTERS    = 0x41 # Sense inverters on TCK and TDO pins of the secondary JTAG port.
_CMD_TMS_TDI            = 0x42 # Send a single TMS and TDI bit.
_CMD_TMS_TDI_TDO        = 0x43 # Send a single TMS and TDI bit and receive TDO bit.
_CMD_TDI_TDO            = 0x44 # Send multiple TDI bits and receive multiple TDO bits.
_CMD_TDO                = 0x45 # Receive multiple TDO bits.
_CMD_TDI                = 0x46 # Send multiple TDI bits.
_CMD_RUNTEST            = 0x47 # Pulse TCK a given number of times.
_CMD_NULL_TDI           = 0x48 # Send string of TDI bits.
_CMD_PROG               = 0x49 # Change the level of the FPGA PROGRAM# pin.
_CMD_SINGLE_TEST_VECTOR = 0x4a # Send a single, byte-wide test vector.
_CMD_GET_TEST_VECTOR    = 0x4b # Read the current test vector being output.
_CMD_SET_OSC_FREQ       = 0x4c # Set the frequency of the DS1075 oscillator.
_CMD_ENABLE_RETURN      = 0x4d # Enable return of info in response to a command.
_CMD_DISABLE_RETURN     = 0x4e # Disable return of info in response to a command.
_CMD_TAP_SEQ            = 0x4f # Send multiple TMS & TDI bits while receiving multiple TDO bits.
_CMD_FLASH_ONOFF        = 0x50 # Enable/disable the FPGA configuration flash.
_CMD_RESET              = 0xff # Cause a power-on reset.

# _CMD_TAP_SEQ flag bits
_GET_TDO_MASK           = 0x01 # Set if gathering TDO bits.
_PUT_TMS_MASK           = 0x02 # Set if TMS bits are included in the packets.
_TMS_VAL_MASK           = 0x04 # Static value for TMS if PUT_TMS_MASK is cleared.
_PUT_TDI_MASK           = 0x08 # Set if TDI bits are included in the packets.
_TDI_VAL_MASK           = 0x10 # Static value for TDI if PUT_TDI_MASK is cleared.

#------------------------------------------------------------------------------
# other usb defines

_VID = 0x04d8
_PID = 0xff8c

_USB_TIMEOUT = 1000 # timeout in milliseconds

#------------------------------------------------------------------------------

def find_device(vid, pid, n):
    """enumerate the bus and find the n-th device with matching vid and pid"""
    instance = 0
    d = None
    for bus in usb.busses():
        for device in bus.devices:
            if device.idVendor == vid and device.idProduct == pid:
                if n == instance:
                    d = device
                    break;
                else:
                    instance += 1
    if d is None:
        raise Error, 'couldn\'t find instance %d of the device' % n
    return d

#------------------------------------------------------------------------------

class usb_dev:

    def __init__(self, n = 0):
        """find the usb device and get the device information"""
        dev = find_device(_VID, _PID, n)
        self.handle = dev.open()
        self.handle.claimInterface(0)
        self.handle.reset()

    def reset_ep(self, ep):
        self.handle.resetEndpoint(usb.ENDPOINT_OUT + ep)
        self.handle.resetEndpoint(usb.ENDPOINT_IN + ep)

    def usb_txrx(self, ep, tx, rx_bytes = 0, check_cmd = False):
        """tx and/or rx usb packets"""
        if tx and len(tx):
            self.handle.bulkWrite(usb.ENDPOINT_OUT + ep, tx, _USB_TIMEOUT)
        if rx_bytes:
            rx = self.handle.bulkRead(usb.ENDPOINT_IN + ep, rx_bytes, _USB_TIMEOUT)
            if len(rx) != rx_bytes:
                raise Error, 'received usb packet is too short'
            if check_cmd and (ord(tx[0]) != rx[0]):
                raise Error, 'command byte in response buffer does not match'
            return rx

    def __del__(self):
        self.handle.releaseInterface()

#-----------------------------------------------------------------------------

class usb_ep:

    def __init__(self, dev, ep):
        self.dev = dev
        self.ep = ep
        self.dev.reset_ep(self.ep)

    def txrx(self, tx, rx_bytes = 0, check_cmd = False):
        """tx/rx to endpoint"""
        return self.dev.usb_txrx(self.ep, tx, rx_bytes, check_cmd)

    def get_device_info(self):
        """get device information"""
        try:
            info = self.dev.usb_txrx(self.ep, utils.b2s((_CMD_INFO, 0)), 32, True)
        except usb.USBError:
            self.power_cycle()
            raise Error, 'unable to read device information'
        return info

    def power_cycle(self):
        """reset the microcontroller of the usb device"""
        self.dev.usb_txrx(self.ep, utils.b2s((_CMD_RESET,) + (0,) * 31))
        time.sleep(4)

#-----------------------------------------------------------------------------
# tms bit sequences

def _tms_bits(bits):
    """convert a left to right bit string to an mpsee (len, bits) tuple"""
    l = list(bits)
    # tms is shifted lsb first
    l.reverse()
    return (len(bits), int(''.join(l), 2) & 255)

# pre-canned jtag state machine transitions
_2reset = _tms_bits('11111') # any state -> reset
_2rti = _tms_bits('111110')  # any state -> run-test/idle
_rti2sir = _tms_bits('1100') # run-test/idle -> shift-ir
_rti2sdr = _tms_bits('100')  # run-test/idle -> shift-dr
_ex2rti = _tms_bits('10')    # exit-x -> run-test/idle

#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, io):
        self.io = io

    def clock_tms(self, bits):
        n = bits[0]
        cmd = [_CMD_TAP_SEQ, n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff, (n >> 24) & 0xff]
        cmd.extend([_PUT_TDI_MASK | _PUT_TMS_MASK, bits[1], 0])
        self.io.txrx(utils.b2s(cmd))

    def shift_data(self, tdi, tdo):
        """
        write (and possibly read) a bit stream from JTAG
        tdi - bit buffer of data to be written to the JTAG TDI pin
        tdo - bit buffer for the data read from the JTAG TDO pin (optional)
        """
        n = len(tdi)
        cmd = [0, n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff, (n >> 24) & 0xff]
        if (tdi.val != 0) and (tdo is None):
            cmd[0] = _CMD_TDI
            self.io.txrx(utils.b2s(cmd))
            self.io.txrx(utils.b2s(tdi.get()))
        elif (tdi.val == 0) and (tdo is not None):
            cmd[0] = _CMD_TDO
            self.io.txrx(utils.b2s(cmd))
            rx = self.io.txrx(None, (n + 7)/8)
            tdo.set(n, rx)
        elif (tdi.val != 0) and (tdo is not None):
            cmd[0] = _CMD_TDI_TDO
            self.io.txrx(utils.b2s(cmd))
            rx = self.io.txrx(utils.b2s(tdi.get()), (n + 7)/8)
            tdo.set(n, rx)
        # exit-x -> run-test/idle
        self.clock_tms(_ex2rti)

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        ## run-test/idle -> shift-ir
        self.clock_tms(_rti2sir)
        self.shift_data(tdi, tdo)

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        ## run-test/idle -> shift-dr
        self.clock_tms(_rti2sdr)
        self.shift_data(tdi, tdo)

    def test_reset(self, val):
        """control the test reset line"""
        pass

    def state_reset(self):
        """goto the reset state"""
        # any state -> reset
        self.clock_tms(_2reset)

    def state_idle(self):
        """goto the idle state"""
        # any state -> run-test/idle
        self.clock_tms(_2rti)

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain to the run-test/idle state"""
        self.state_idle()

    def __str__(self):
        """return a string describing the device"""
        return 'xsusb'

#------------------------------------------------------------------------------