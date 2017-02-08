#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# 
# For more information, please refer to <http://unlicense.org>
# 

import numpy
from gnuradio import gr
import pmt
import array
import struct

class check_address(gr.basic_block):
    """
    docstring for block check_address
    """
    def __init__(self, address, direction):
        gr.basic_block.__init__(self,
            name="check_address",
            in_sig=[],
            out_sig=[])

        a = address.split('-')
        self.callsign = a[0]
        self.ssid = int(a[1]) if len(a) > 1 else None
        self.direction = direction
        
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.message_port_register_out(pmt.intern('ok'))
        self.message_port_register_out(pmt.intern('fail'))

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return
        packet = array.array("B", pmt.u8vector_elements(msg))

        # check packet length
        # an AX.25 header with 2 addresses, control and PID is 16 bytes
        if len(packet) < 16:
            self.message_port_pub(pmt.intern('fail'), msg_pmt)
            return

        if self.direction == 'to':
            address = packet[:7]
        else:
            address = packet[7:14]

        callsign = array.array('B', map(lambda c: c >> 1, address[:6])).tostring().rstrip(' ')
        ssid = int((address[6] >> 1) & 0x0f)

        if callsign != self.callsign or (self.ssid != None and ssid != self.ssid):
            # incorrect address
            self.message_port_pub(pmt.intern('fail'), msg_pmt)
        else:
            # correct address
            self.message_port_pub(pmt.intern('ok'), msg_pmt)
