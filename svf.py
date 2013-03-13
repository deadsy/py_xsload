# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
"""
SVF File Interpreter
"""
#------------------------------------------------------------------------------

import time
import os

import utils
import bits

#------------------------------------------------------------------------------

class Error(Exception):
    pass

#------------------------------------------------------------------------------

class svf:

    def __init__(self, filename, jtag):
        self.filename = filename
        self.jtag = jtag
        self.tck_period = 0.0

    def cmd_state(self, args):
        """transition through specific jtag states"""
        func = {
            'RESET': self.jtag.driver.state_reset,
            'IDLE': self.jtag.driver.state_idle,
        }
        for state in args[1:]:
            if not func.has_key(state):
                raise Error, 'line %d: unknown jtag state %s' % (self.line, state)
            func[state]()

    def parse_tdi_tdo(self, args):
        """
        parse: length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]
        return the values in a dictionary
        """
        vals = dict(zip(args[1::2], [utils.unparen(v) for v in args[2::2]]))
        vals['NBITS'] = int(args[0])
        if not vals.has_key('TDI'):
            raise Error, 'line %d: missing TDI parameter' % self.line
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
            if tdo != tdo_expected:
                raise Error, 'line %d: tdo actual/expected mismatch' % self.line

    def cmd_todo(self, args):
        """command not implemented"""
        print('line %d: %s (todo)' % (self.line, ' '.join(args)))

    def cmd_unknown(self, args):
        """command unknown"""
        raise Error, 'line %d: unknown command - "%s"' % (self.line, args[0])

    def cmd_chain(self, args):
        """ignore chain context commands"""
        if int(args[1]) != 0:
            raise Error, 'line %d: no support for non-zero %s length' % (self.line, args[0])

    def cmd_frequency(self, args):
        if args[2] != 'HZ':
            raise Error, 'line %d: unrecognized %s unit - "%s"' % (self.line, args[0], args[2])
        self.tck_period = 1.0 / float(args[1])

    def cmd_sir(self, args):
        """command: SIR length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]"""
        vals = self.parse_tdi_tdo(args[1:])
        tdi = bits.bits(vals['NBITS'], vals['TDI'])
        if vals.has_key('TDO'):
            tdo = bits.bits()
            self.jtag.rw_ir(tdi, tdo)
            self.validate_tdo(tdo, vals)
        else:
            self.jtag.wr_ir(tdi)

    def cmd_sdr(self, args):
        """command: SDR length TDI (tdi) SMASK (smask) [TDO (tdo) MASK (mask)]"""
        vals = self.parse_tdi_tdo(args[1:])
        tdi = bits.bits(vals['NBITS'], vals['TDI'])
        if vals.has_key('TDO'):
            tdo = bits.bits()
            self.jtag.rw_dr(tdi, tdo)
            self.validate_tdo(tdo, vals)
        else:
            self.jtag.wr_dr(tdi)

    def cmd_end_state(self, args):
        """specify the ending state for the sdr/sir command"""
        if args[1] != 'IDLE':
            raise Error, 'line %d: unrecognized %s value - "%s"' % (self.line, args[0], args[1])

    def cmd_runtest(self, args):
        """command: RUNTEST run_count TCK"""
        if args[2] != 'TCK':
            raise Error, 'line %d: unrecognized %s unit - "%s"' % (self.line, args[0], args[2])
        time.sleep(2.0 * self.tck_period * int(args[1]))

    def cmd_trst(self, args):
        if not (args[1] in ('OFF', 'ON')):
            raise Error, 'line %d: unrecognized %s value - "%s"' % (self.line, args[0], args[1])
        self.jtag.driver.test_reset(args[1] == 'ON')

    def playback(self):
        """playback an svf file through the jtag device"""
        self.line = 0
        progress = utils.progress(300, os.path.getsize(self.filename))
        f = open(self.filename, 'r')
        funcs = {
            'SDR': self.cmd_sdr,
            'HDR': self.cmd_chain,
            'TDR': self.cmd_chain,
            'ENDDR': self.cmd_end_state,
            'SIR': self.cmd_sir,
            'HIR': self.cmd_chain,
            'TIR': self.cmd_chain,
            'ENDIR': self.cmd_end_state,
            'RUNTEST': self.cmd_runtest,
            'TRST': self.cmd_trst,
            'STATE': self.cmd_state,
            'FREQUENCY': self.cmd_frequency,
        }
        for l in f:
            self.line += 1
            l = l.strip()
            if l.startswith('//') or len(l) == 0:
                continue
            if not l.endswith(';'):
                raise Error, 'line %d: missing ; at end of line' % self.line
            l = l.rstrip(';')
            args = l.split()
            #print('line %d: %s' % (self.line, ' '.join(args)))
            funcs.get(args[0], self.cmd_unknown)(args)
            progress.update(f.tell())
        progress.erase()
        f.close()

#------------------------------------------------------------------------------
