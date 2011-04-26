# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
SVF File Interpreter
"""
#------------------------------------------------------------------------------

import time

import utils
import bits

#------------------------------------------------------------------------------

class svf:

    def __init__(self, filename, device):
        self.filename = filename
        self.device = device
        self.tck_period = 0.0

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
            n = vals['NBITS']
            tdo_expected = bits.bits(n, vals['TDO'])
            if vals.has_key('MASK'):
                mask = bits.bits(n, vals['MASK'])
                tdo &= mask
                tdo_expected &= mask
            return tdo == tdo_expected
        else:
            return True

    def cmd_todo(self, args):
        """command not implemented"""
        return True

    def cmd_unknown(self, args):
        """command unknown"""
        self.errors.append('line %d: unknown command - "%s"' % (self.line, args[0]))
        return True

    def cmd_chain(self, args):
        """ignore chain context commands"""
        if args[1] != 0:
            self.errors.append('line %d: non support for non-zero %s length' % (self.line, args[0]))
        return True

    def cmd_frequency(self, args):
        if args[2] != 'HZ':
            self.errors.append('line %d: unrecognized %s unit - "%s"' % (self.line, args[0], args[2]))
        self.tck_period = 1.0 / float(args[1])
        return True

    def cmd_sdr_sir(self, args):
        """command: SDR/SIR length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]"""
        vals = self.parse_tdi_tdo(args[1:])
        tdi = bits.bits(vals['NBITS'], vals['TDI'])
        tdo = (None, bits.bits())[vals.has_key('TDO')]
        if args[0] == 'SDR':
            self.device.scan_dr(tdi, tdo)
        else:
            self.device.scan_ir(tdi, tdo)
        return self.validate_tdo(tdo, vals)

    def cmd_runtest(self, args):
        """command: RUNTEST run_count TCK"""
        if args[2] != 'TCK':
            self.errors.append('line %d: unrecognized %s unit - "%s"' % (self.line, args[0], args[2]))
        time.sleep(2.0 * self.tck_period * int(args[1]))
        return True

    def playback(self):
        """playback an svf file through the jtag device"""
        self.errors = []
        self.line = 0
        f = open(self.filename, 'r')
        errors = []
        funcs = {
            'SDR': self.cmd_sdr_sir,
            'HDR': self.cmd_chain,
            'TDR': self.cmd_chain,
            'ENDDR': self.cmd_todo,
            'SIR': self.cmd_sdr_sir,
            'HIR': self.cmd_chain,
            'TIR': self.cmd_chain,
            'ENDIR': self.cmd_todo,
            'RUNTEST': self.cmd_runtest,
            'TRST': self.cmd_todo,
            'STATE': self.cmd_todo,
            'FREQUENCY': self.cmd_frequency,
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
