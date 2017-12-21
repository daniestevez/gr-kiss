#!/usr/bin/env python

import numpy
from gnuradio import gr
import collections
import pmt
import array
import zmq
import thread


class frame_sink(gr.basic_block):
    """
    docstring for block hdlc_framer
    """
    def __init__(self, address):
        gr.basic_block.__init__(self,
            name="frame_sink",
            in_sig=None,
            out_sig=None)

        self.address = address
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        print "Address: |%s|" % address
        self.socket.bind(address)

    def handle_msg(self, msg_pmt):
        print "HANDLE", msg_pmt
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return

        data = list(pmt.u8vector_elements(msg))
        data = "".join(map(chr, data))
        self.socket.send(data)
