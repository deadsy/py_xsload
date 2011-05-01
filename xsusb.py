# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
XSUSB JTAG Driver - JTAG via USB and a Microcontroller
"""
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# command set

_CMD_READ_VERSION_CMD       = 0x00 # Read the product version information.
_CMD_READ_FLASH_CMD         = 0x01 # Read from the device flash.
_CMD_WRITE_FLASH_CMD        = 0x02 # Write to the device flash.
_CMD_ERASE_FLASH_CMD        = 0x03 # Erase the device flash.
_CMD_READ_EEDATA_CMD        = 0x04 # Read from the device EEPROM.
_CMD_WRITE_EEDATA_CMD       = 0x05 # Write to the device EEPROM.
_CMD_READ_CONFIG_CMD        = 0x06 # Read from the device configuration memory.
_CMD_WRITE_CONFIG_CMD       = 0x07 # Write to the device configuration memory.
_CMD_ID_BOARD_CMD           = 0x31 # Flash the device LED to identify which device is being communicated with.
_CMD_UPDATE_LED_CMD         = 0x32 # Change the state of the device LED.
_CMD_INFO_CMD               = 0x40 # Get information about the USB interface.
_CMD_SENSE_INVERTERS_CMD    = 0x41 # Sense inverters on TCK and TDO pins of the secondary JTAG port.
_CMD_TMS_TDI_CMD            = 0x42 # Send a single TMS and TDI bit.
_CMD_TMS_TDI_TDO_CMD        = 0x43 # Send a single TMS and TDI bit and receive TDO bit.
_CMD_TDI_TDO_CMD            = 0x44 # Send multiple TDI bits and receive multiple TDO bits.
_CMD_TDO_CMD                = 0x45 # Receive multiple TDO bits.
_CMD_TDI_CMD                = 0x46 # Send multiple TDI bits.
_CMD_RUNTEST_CMD            = 0x47 # Pulse TCK a given number of times.
_CMD_NULL_TDI_CMD           = 0x48 # Send string of TDI bits.
_CMD_PROG_CMD               = 0x49 # Change the level of the FPGA PROGRAM# pin.
_CMD_SINGLE_TEST_VECTOR_CMD = 0x4a # Send a single, byte-wide test vector.
_CMD_GET_TEST_VECTOR_CMD    = 0x4b # Read the current test vector being output.
_CMD_SET_OSC_FREQ_CMD       = 0x4c # Set the frequency of the DS1075 oscillator.
_CMD_ENABLE_RETURN_CMD      = 0x4d # Enable return of info in response to a command.
_CMD_DISABLE_RETURN_CMD     = 0x4e # Disable return of info in response to a command.
_CMD_TAP_SEQ_CMD            = 0x4f # Send multiple TMS & TDI bits while receiving multiple TDO bits.
_CMD_FLASH_ONOFF_CMD        = 0x50 # Enable/disable the FPGA configuration flash.
_CMD_RESET_CMD              = 0xff # Cause a power-on reset.

#------------------------------------------------------------------------------

class jtag_driver:

    def __init__(self, port):
        self.port = port


#------------------------------------------------------------------------------