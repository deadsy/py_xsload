# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Bitfile Loader
"""
#------------------------------------------------------------------------------

import time
import os
import struct

import utils

#------------------------------------------------------------------------------

class Error(Exception):
    pass

#------------------------------------------------------------------------------

def strip_header(data):
    """remove the header from the file"""
    hdr_len = 4 + struct.unpack('>H', data[:2])[0]
    if struct.unpack('>H', data[hdr_len - 2:hdr_len])[0] != 1:
        raise Error, 'invalid bit file header for %s' % self.filename
    return data[hdr_len:]

#------------------------------------------------------------------------------

def get_tlv(t, data):
    """return the value for tlv with type t"""
    max_len = len(data)
    i = 0
    while  i < max_len:
        tlv_t = ord(data[i])
        i += 1
        if tlv_t in (0x61, 0x62, 0x63, 0x64):
            tlv_l = struct.unpack('>H', data[i: i + 2])[0]
            i += 2
        elif tlv_t in (0x65,):
            tlv_l = struct.unpack('>I', data[i: i + 4])[0]
            i += 4
        else:
            raise Error, 'unrecognized tlv type 0x%02x' % tlv_t
        if tlv_t == t:
            return data[i: i + tlv_l]
        i += tlv_l
    raise Error, 'couldn\'t find tlv with type 0x%02x' % t

#------------------------------------------------------------------------------

def load(filename, smap):
    f = open(filename, 'r')
    data = f.read()
    f.close()
    data = strip_header(data)
    print('part: %s' % get_tlv(0x62, data))
    print('created: %s at %s' % (get_tlv(0x63, data), get_tlv(0x64, data)))
    bitstream = get_tlv(0x65, data)
    print('bitstream: %d bytes' % len(bitstream))
    # write out the bitstream
    progress = utils.progress(100, len(bitstream))
    i = 0
    smap.start()
    for byte in bitstream:
        smap.wr(ord(byte))
        progress.update(i)
        i += 1
    smap.finish()
    progress.erase()

#------------------------------------------------------------------------------
