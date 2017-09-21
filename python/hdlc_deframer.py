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

import hdlc

def pack(s):
    d = bytearray()
    for i in range(0, len(s), 8):
        x = 0
        for j in range(7,-1,-1): # LSB first
            x <<= 1
            x += s[i+j]
        d.append(x)
    return d

def fcs_ok(frame):
    if len(frame) <= 2: return False
    crc = hdlc.crc_ccitt(frame[:-2])
    return frame[-2] == (crc & 0xff) and frame[-1] == ((crc >> 8) & 0xff)

class hdlc_deframer(gr.sync_block):
    """
    docstring for block hdlc_deframer
    """
    def __init__(self, check_fcs, trim_fcs, max_length):
        gr.sync_block.__init__(self,
            name="hdlc_deframer",
            in_sig=[numpy.uint8],
            out_sig=None)

        self.bits = collections.deque(maxlen = (max_length+2)*8 + 7)
        self.ones = 0  # consecutive ones for flag checking
        self.check = check_fcs
        self.trim_fcs = trim_fcs

        self.message_port_register_out(pmt.intern('out'))

    def work(self, input_items, output_items):
        in0 = input_items[0]

        for x in in0:
            if x:
                self.ones += 1
                self.bits.append(x)
            else:
                if self.ones == 5:
                    # destuff = do nothing
                    None
                elif self.ones > 5: # should be ones == 6 unless packet is corrupted
                    # flag received
                    # prepare to send frame
                    for _ in range(min(7, len(self.bits))):
                                   self.bits.pop() # remove 7 previous flag bits
                    if len(self.bits) % 8:
                        # pad on the left with 0's
                        self.bits.extendleft([0] * (8 - len(self.bits) % 8))
                    frame = pack(self.bits)
                    self.bits.clear()
                    if frame and (not self.check or fcs_ok(frame)):
                        # send frame
                        if self.trim_fcs:
                            frame = frame[:-2]
                        buff = array.array('B', frame)
                        self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(buff), buff)))
                else:
                    self.bits.append(x)
                self.ones = 0
                
        return len(input_items[0])

