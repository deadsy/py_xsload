# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
"""
Parallel Port IO for a bitbang JTAG

This is a slow interface - with a simple loop the maximum observed
clock rate for any IO pin is around 150KHz

"""
#-----------------------------------------------------------------------------

import parallel

#-----------------------------------------------------------------------------

class io:

    def __init__(self, port):
        self.p = parallel.Parallel(port)
        self.p.PPDATADIR(True)

    def rd_ctrl(self, b):
        """read ctrl byte"""
        self.p.PPRCONTROL(b)

    def wr_ctrl(self, b):
        """write ctrl byte"""
        self.p.PPWCONTROL(b)

    def wr_data(self, b):
        """write data byte"""
        self.p.PPWDATA(b)

    def rd_status(self):
        """read status byte"""
        return self.p.PPRSTATUS()


#-----------------------------------------------------------------------------
