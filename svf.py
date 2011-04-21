# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
SVF File Interpreter
"""
#------------------------------------------------------------------------------

class virtual_jtag:

    def __init__(self):
        pass

    def scan_ir(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the IR in the JTAG chain"""
        pass

    def scan_dr(self, tdi, tdo = None):
        """write (and possibly read) a bit stream through the DR in the JTAG chain"""
        pass

    def set_frequency(self, f):
        """set the tck frequency"""
        pass

    def delay(self, n):
        """delay n tck cycles"""
        print 'delay %d tck cycles' % n

#------------------------------------------------------------------------------

def unparen(x):
    """string (hex-number) to integer"""
    return long(x[1:-1], 16)

class svf:

    def __init__(self, filename, jtag):
        self.filename = filename
        self.jtag = jtag

    def parse_tdi_tdo(self, parms, n):
        """length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]"""
        x = parms.split()
        vals = dict(zip(x[1::2], [unparen(v) for v in x[2::2]]))
        vals['NBITS'] = int(x[0])
        if not vals.has_key('TDI'):
            self.errors.append('line %d: missing TDI parameter' % n)
        return vals

    def cmd_do_nothing(self, cmd, parms, n):
        pass

    def cmd_unknown(self, cmd, parms, n):
        self.errors.append('line %d: unrecognised command - "%s"' % (n, cmd))

    def cmd_sir(self, cmd, parms, n):
        """SIR length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]"""
        print('line %d: %s %s' % (n, cmd, parms))
        vals = self.parse_tdi_tdo(parms, n)
        #tdi = bits.bitbuffer(vals['NBITS'], val['TDI'])
        self.jtag.scan_ir(None)

    def cmd_sdr(self, cmd, parms, n):
        """SDR length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]"""
        print('line %d: %s %s' % (n, cmd, parms))
        vals = self.parse_tdi_tdo(parms, n)
        self.jtag.scan_dr(None)

    def cmd_runtest(self, cmd, parms, n):
        """RUNTEST run_count TCK"""
        x = parms.split(' ', 1)
        if x[1] != 'TCK':
            self.errors.append('line %d: unrecognised RUNTEST unit - "%s"' % (n, x[1]))
        self.jtag.delay(int(x[0]))

    def playback(self):
        self.errors = []
        f = open(self.filename, 'r')
        n = 0
        errors = []
        funcs = {
            'SDR': self.cmd_sdr,
            'HDR': self.cmd_do_nothing,
            'TDR': self.cmd_do_nothing,
            'ENDDR': self.cmd_do_nothing,
            'SIR': self.cmd_sir,
            'HIR': self.cmd_do_nothing,
            'TIR': self.cmd_do_nothing,
            'ENDIR': self.cmd_do_nothing,
            'RUNTEST': self.cmd_runtest,
            'TRST': self.cmd_do_nothing,
            'STATE': self.cmd_do_nothing,
            'FREQUENCY': self.cmd_do_nothing,
        }
        for l in f:
            n += 1
            l = l.strip()
            if l.startswith('//'):
                continue
            if not l.endswith(';'):
                self.errors.append('line %d: missing ; at end of line' % n)
                continue
            l = l.rstrip(';')
            x = l.split(' ', 1)
            funcs.get(x[0], self.cmd_unknown)(x[0], x[1], n)
        f.close()
        return self.errors

#------------------------------------------------------------------------------

x = svf('dwnldpar.svf', virtual_jtag())
e = x.playback()
if len(e):
    print '\n'.join(e)
else:
    print 'no errors'
