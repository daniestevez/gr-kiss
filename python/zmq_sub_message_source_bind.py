#!/usr/bin/env python

import numpy
from gnuradio import gr
import collections
import pmt
import array
import zmq
import thread


class zmq_sub_message_source_bind(gr.basic_block):
    """
    docstring for block hdlc_framer
    """
    def __init__(self, address):
        gr.basic_block.__init__(self,
            name="zmq_sub_message_source_bind",
            in_sig=None,
            out_sig=None)

        self.address = address
        self.message_port_register_out(pmt.intern('out'))

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        print "Address: |%s|" % address
        self.socket.bind(address)
        self.socket.setsockopt(zmq.SUBSCRIBE, "")

        thread.start_new_thread(self.loop, ())

    def loop(self):
        while True:
            if self.socket.poll(timeout=1) > 0:
                output_items = self.socket.recv()

                pkt = pmt.deserialize_str(output_items)

                self.message_port_pub(pmt.intern('out'), pkt)
