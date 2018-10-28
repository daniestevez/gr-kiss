# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Frequency Shift
# Author: Grzegorz Gajoch
# Generated: Sun Oct 28 19:21:11 2018
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes

from gr_kiss import *

class frequency_shift(gr.hier_block2):

    def __init__(self, bw=0, center_frequency=0, samp_rate=0, transition_width=0, decimation=1):
        gr.hier_block2.__init__(
            self, "Frequency Shift",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.bw = bw
        self.center_frequency = center_frequency
        self.samp_rate = samp_rate
        self.transition_width = transition_width
        self.decimation = decimation

        ##################################################
        # Blocks
        ##################################################
        self.low_pass_filter_0 = filter.fir_filter_ccf(decimation, firdes.low_pass(
        	1, samp_rate, bw, transition_width, firdes.WIN_HANN, 6.76))
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_sig_source_x_1 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, -center_frequency, 1, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self, 0))
        self.connect((self, 0), (self.blocks_multiply_xx_0, 0))

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.bw, self.transition_width, firdes.WIN_HANN, 6.76))

    def get_center_frequency(self):
        return self.center_frequency

    def set_center_frequency(self, center_frequency):
        self.center_frequency = center_frequency
        self.analog_sig_source_x_1.set_frequency(-self.center_frequency)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.bw, self.transition_width, firdes.WIN_HANN, 6.76))
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)

    def get_transition_width(self):
        return self.transition_width

    def set_transition_width(self, transition_width):
        self.transition_width = transition_width
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.bw, self.transition_width, firdes.WIN_HANN, 6.76))

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
