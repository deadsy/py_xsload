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
        self.handle.reset()
        self.get_device_info()

    def get_device_info(self):
        """get device information"""
        msg = utils.b2s((_CMD_INFO, 0))
        self.handle.bulkWrite(usb.ENDPOINT_OUT + 1, msg, _USB_TIMEOUT)
        try:
            info = self.handle.bulkRead(usb.ENDPOINT_IN + 1, 32, _USB_TIMEOUT)
        except usb.USBError:
            self.power_cycle()
            raise Error, 'unable to read device information'
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

    def power_cycle(self):
        """reset the microcontroller of the usb device"""
        msg = utils.b2s((_CMD_RESET,) + (0,) * 31)
        self.handle.bulkWrite(usb.ENDPOINT_OUT + 1, msg, _USB_TIMEOUT)
        time.sleep(4)

    def clock_tms(self, tms):
        """clock out a tms bit"""
        msg = utils.b2s((_CMD_TMS_TDI, tms))
        self.handle.bulkWrite(usb.ENDPOINT_OUT + 1, msg, _USB_TIMEOUT)

    def clock_data_io(self, tms, tdi):
        """clock out tdi bit, sample tdo bit"""
        msg = utils.b2s((_CMD_TMS_TDI_TDO, (tdi << 1) | tms))
        self.handle.bulkWrite(usb.ENDPOINT_OUT + 1, msg, _USB_TIMEOUT)
        rx = self.handle.bulkRead(usb.ENDPOINT_IN + 1, 2, _USB_TIMEOUT)
        return (rx[1] >> 2) & 1

    def clock_data_o(self, tms, tdi):
        """clock out tdi bit"""
        msg = utils.b2s((_CMD_TMS_TDI, (tdi << 1) | tms))
        self.handle.bulkWrite(usb.ENDPOINT_OUT + 1, msg, _USB_TIMEOUT)

    def __del__(self):
        self.handle.releaseInterface()

    def __str__(self):
        return '%s version %s/%d' % (self.name, self.version, self.pid)


#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, io):
        self.io = io

    def shift_data(self, tdi, tdo):
        """
        write (and possibly read) a bit stream from JTAG
        tdi - bit buffer of data to be written to the JTAG TDI pin
        tdo - bit buffer for the data read from the JTAG TDO pin (optional)
        """
        if tdo is None:
            for i in range(tdi.n - 1):
                self.io.clock_data_o(0, tdi.shr())
            # last bit
            self.io.clock_data_o(1, tdi.shr())
        else:
            tdo.zeroes(tdi.n)
            for i in range(tdi.n - 1):
                tdo.shr(self.io.clock_data_io(0, tdi.shr()))
            # last bit
            tdo.shr(self.io.clock_data_io(1, tdi.shr()))
        # shift-x -> run-test/idle
        self.io.clock_tms(1)
        self.io.clock_tms(0)

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        _log.debug('jtag.scan_ir()')
        ## run-test/idle -> shift-ir
        [self.io.clock_tms(x) for x in (1,1,0,0)]
        self.shift_data(tdi, tdo)

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        _log.debug('jtag.scan_dr()')
        ## run-test/idle -> shift-dr
        [self.io.clock_tms(x) for x in (1,0,0)]
        self.shift_data(tdi, tdo)

    def state_reset(self):
        """goto the reset state"""
        # any state -> reset
        [self.io.clock_tms(x) for x in (1,1,1,1,1)]

    def state_idle(self):
        """goto the idle state"""
        # any state -> run-test/idle
        [self.io.clock_tms(x) for x in (1,1,1,1,1,0)]

    def reset_jtag(self):
        """reset the TAP of all JTAG devices in the chain to the run-test/idle state"""
        _log.debug('jtag.reset_jtag()')
        self.state_idle()

    def __str__(self):
        """return a string describing the device"""
        return str(self.io)

#------------------------------------------------------------------------------