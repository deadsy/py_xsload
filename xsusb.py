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

_log = logging.getLogger('xsusb')
#_log.setLevel(logging.DEBUG)

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

# command response lengths
_CMD_INFO_LEN = 32

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

class xsusb:

    def __init__(self, n = 0):
        """find the xsusb device and get the device information"""
        dev = find_device(_VID, _PID, n)
        self.handle = dev.open()
        self.handle.claimInterface(0)
        self.handle.resetEndpoint(usb.ENDPOINT_OUT + 1)
        self.handle.resetEndpoint(usb.ENDPOINT_IN + 1)
        self.handle.reset() # ??
        # get device information
        msg = utils.b2s((_CMD_INFO, 0))
        self.handle.bulkWrite(usb.ENDPOINT_OUT + 1, msg, _USB_TIMEOUT)
        try:
            info = self.handle.bulkRead(usb.ENDPOINT_IN + 1, _CMD_INFO_LEN, _USB_TIMEOUT)
        except usb.USBError:
            self.reset()
            raise Error, 'unable to read device information'
        self.info = info

    def reset(self):
        print 'resetting'
        msg = utils.b2s((_CMD_RESET,) + (0,) * 31)
        self.handle.bulkWrite(usb.ENDPOINT_OUT + 1, msg, _USB_TIMEOUT)
        time.sleep(4)

    def __del__(self):
        self.handle.releaseInterface()

#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, io):
        self.io = io

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        _log.debug('jtag.scan_ir()')
        ## run-test/idle -> shift-ir
        #self.clock_tms(1)
        #self.clock_tms(1)
        #self.clock_tms(0)
        #self.clock_tms(0)
        #self.shift_data(tdi, tdo)

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        _log.debug('jtag.scan_dr()')
        ## run-test/idle -> shift-dr
        #self.clock_tms(1)
        #self.clock_tms(0)
        #self.clock_tms(0)
        #self.shift_data(tdi, tdo)

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain to the run-test/idle state"""
        _log.debug('jtag.reset_jtag()')
        #self.test_reset(True)
        #time.sleep(_TRST_TIME)
        #self.test_reset(False)
        #self.state_idle()

    def __str__(self):
        """return a string describing the device"""
        return 'xsusb'

#------------------------------------------------------------------------------