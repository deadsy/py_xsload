# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
Bitfile Loader
"""
#------------------------------------------------------------------------------

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
# See Xilinx XAPP452

def decode(filename):
    """decode a bitfile"""

    dummy_word = 0xffffffff
    sync_word = 0xaa995566
    noop_word = 0x20000000

    def hdr_type(x):
        return (x >> 29) & 7
    def hdr_op(x):
        return (x >> 27) & 3
    def hdr_t1_adr(x):
        return (x >> 13) & 0x3fff
    def hdr_t1_words(x):
        return x & 0x7ff
    def hdr_t2_words(x):
        return x & 0x7ffffff

    def adr2name(x):
        a2n = {0: 'crc', 1: 'far', 2: 'fdri', 3: 'fdro', 4: 'cmd',
               5: 'ctl', 6: 'mask',7: 'stat', 8: 'lout', 9: 'cor',
               10: 'mfwr',11: 'flr',14: 'idcode',}
        return a2n.get(x, '?? (%d)' % x)

    def cmd2name(x):
        c2n = {0: 'null', 1: 'wcfg', 2: 'mfwr', 3: 'dghigh/lfrm', 4: 'rcfg',
               5: 'start', 6: 'rcap', 7: 'rcrc', 8: 'aghigh', 9: 'switch',
               10: 'grestore', 11: 'shutdown', 12: 'gcapture', 13:'desynch',}
        return c2n.get(x, '?? (%d)' % x)

    f = open(filename, 'r')
    data = f.read()
    f.close()
    data = strip_header(data)
    print('part: %s' % get_tlv(0x62, data))
    print('created: %s at %s' % (get_tlv(0x63, data), get_tlv(0x64, data)))
    bitstream = get_tlv(0x65, data)
    print('bitstream: %d bytes' % len(bitstream))

    # decode the bitstream
    i = 0
    t2_flag = False
    auto_crc_flag = False
    noop_count = 0

    while i < len(bitstream):
        s = []
        #s .append('%d' % i)
        x = struct.unpack('>I', bitstream[i: i + 4])[0]
        i += 4
        s.append('%08x:' % x)

        if t2_flag:
            if hdr_type(x) == 2:
                s.append('t2 op %d' % hdr_op(x))
                words = hdr_t2_words(x)
                s.append('words %d ...' % words)
                i += (words << 2)
            else:
                s.append('expected a t2 header!')
            t2_flag = False
            auto_crc_flag = True
            print(' '.join(s))
            continue

        if auto_crc_flag:
            s.append('auto crc')
            auto_crc_flag = False
            print(' '.join(s))
            continue

        if noop_count:
            if x != noop_word:
                print('%s noop (x %d)' % (noop_prefix, noop_count))
                noop_count = 0
                i -= 4
            else:
                noop_count += 1
                if i == len(bitstream):
                    print('%s noop (x %d)' % (noop_prefix, noop_count))
            continue

        if x == noop_word:
            noop_prefix = ' '.join(s)
            noop_count = 1
            continue
        elif x == dummy_word:
            s.append('dummy')
        elif x == sync_word:
            s.append('sync')
        elif hdr_type(x) == 1:
            s.append('t1 op %d' % hdr_op(x))
            adr = hdr_t1_adr(x)
            s.append('%s' % adr2name(adr))
            words = hdr_t1_words(x)
            if words == 1:
                val = struct.unpack('>I', bitstream[i: i + 4])[0]
                if adr == 4:
                    s.append('%s' % cmd2name(val))
                else:
                    s.append('0x%08x' % val)
            elif words > 1:
                s.append('words %d ...' % words)
            i += (words << 2)
            if words == 0:
                t2_flag = True
        else:
            s.append('??')
        print(' '.join(s))

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
