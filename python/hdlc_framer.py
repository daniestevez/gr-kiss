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

class hdlc_framer(gr.basic_block):
    """
    docstring for block hdlc_framer
    """
    def __init__(self, preamble_bytes, postamble_bytes):
        gr.basic_block.__init__(self,
            name="hdlc_framer",
            in_sig=None,
            out_sig=None)

        self.preamble_bytes = preamble_bytes
        self.postamble_bytes = postamble_bytes
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.message_port_register_out(pmt.intern('out'))

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return

        data = list(pmt.u8vector_elements(msg))
        crc = hdlc.crc_ccitt(data)
        data.append(crc & 0xff)
        data.append((crc >> 8) & 0xff)
                
        buff = hdlc.flag * self.preamble_bytes
        ones = 0 # number of consecutive ones
        for byte in data:
            for _ in range(8):
                # transmit byte LSB first
                x = byte & 1
                buff.append(x)
                if x:
                    ones += 1
                else:
                    ones = 0
                if ones == 5:
                    # bit-stuff
                    buff.append(0)
                    ones = 0
                byte >>= 1
        buff.extend(hdlc.flag * self.postamble_bytes)

        buff = array.array('B', buff)

        self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(buff), buff)))
