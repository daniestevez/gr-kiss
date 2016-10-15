#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2016 Daniel Estevez <daniel@destevez.net>.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy
from gnuradio import gr
import collections
import pmt
import array

from kiss import *

class kiss_to_pdu(gr.sync_block):
    """
    docstring for block kiss_to_pdu
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="kiss_to_pdu",
            in_sig=[numpy.uint8],
            out_sig=[])

        self.kiss = collections.deque()
        self.pdu = list()
        self.transpose = False

        self.message_port_register_out(pmt.intern('out'))

    def work(self, input_items, output_items):
#    def handle_msg(self, msg_pmt):
        self.kiss.extend(input_items[0])
        
        while self.kiss:
            c = self.kiss.popleft()
            if c == FEND:
                if self.pdu and not self.pdu[0] & 0x0f:
                    msg = array.array('B', self.pdu[1:])
                    self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(msg), msg)))
                self.pdu = list()
            elif self.transpose:
                if c == TFEND:
                    self.pdu.append(FEND)
                elif c == TFESC:
                    self.pdu.append(FESC)
                self.transpose = False
            elif c == FESC:
                self.transpose = True
            else:
                self.pdu.append(c)

        return len(input_items[0])

