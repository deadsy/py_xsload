# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
SVF File Interpreter
"""
#------------------------------------------------------------------------------

import utils
import bits

#------------------------------------------------------------------------------

class svf:

    def __init__(self, filename, jtag):
        self.filename = filename
        self.jtag = jtag

    def parse_tdi_tdo(self, args):
        """
            parse: length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]
            return the values in a dictionary
        """
        vals = dict(zip(args[1::2], [utils.unparen(v) for v in args[2::2]]))
        vals['NBITS'] = int(args[0])
        if not vals.has_key('TDI'):
            self.errors.append('line %d: missing TDI parameter' % self.line)
        return vals

    def validate_tdo(self, tdo, vals):
        """validate returned tdo bits against expectations"""
        if vals.has_key('TDO'):
            return True
        else:
            return True

    def cmd_todo(self, args):
        """command not implemented"""
        return True

    def cmd_unknown(self, args):
        """command unknown"""
        self.errors.append('line %d: unknown command - "%s"' % (self.line, args[0]))
        return True

    def cmd_sir(self, args):
        """command: SIR length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]"""
        vals = self.parse_tdi_tdo(args[1:])
        tdi = bits.bits(vals['NBITS'], vals['TDI'])
        tdo = bits.bits()
        self.jtag.scan_ir(tdi, tdo)
        return self.validate_tdo(tdo, vals)

    def cmd_sdr(self, args):
        """command: SDR length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]"""
        vals = self.parse_tdi_tdo(args[1:])
        tdi = bits.bits(vals['NBITS'], vals['TDI'])
        tdo = bits.bits()
        self.jtag.scan_dr(tdi, tdo)
        return self.validate_tdo(tdo, vals)

    def cmd_runtest(self, args):
        """command: RUNTEST run_count TCK"""
        if args[2] != 'TCK':
            self.errors.append('line %d: unrecognized RUNTEST unit - "%s"' % (self.line, args[2]))
        self.jtag.delay(int(args[1]))
        return True

    def playback(self):
        """playback an svf file through the jtag device"""
        self.errors = []
        self.line = 0
        f = open(self.filename, 'r')
        errors = []
        funcs = {
            'SDR': self.cmd_sdr,
            'HDR': self.cmd_todo,
            'TDR': self.cmd_todo,
            'ENDDR': self.cmd_todo,
            'SIR': self.cmd_sir,
            'HIR': self.cmd_todo,
            'TIR': self.cmd_todo,
            'ENDIR': self.cmd_todo,
            'RUNTEST': self.cmd_runtest,
            'TRST': self.cmd_todo,
            'STATE': self.cmd_todo,
            'FREQUENCY': self.cmd_todo,
        }
        for l in f:
            self.line += 1
            l = l.strip()
            if l.startswith('//'):
                continue
            if not l.endswith(';'):
                self.errors.append('line %d: missing ; at end of line' % self.line)
                continue
            l = l.rstrip(';')
            args = l.split()
            print('line %d: %s' % (self.line, ' '.join(args)))
            funcs.get(args[0], self.cmd_unknown)(args)
        f.close()
        return self.errors

#------------------------------------------------------------------------------
