import numpy
from gnuradio import gr
import serial
from threading import Timer
from time import sleep

class pwsat2_ptt(gr.sync_block):
    """
    This block is used to control PTT state by serial interface. 

    The transciever's PTT input is wired to RTS signal of COM port. Low state ("False") is receive, High state ("True") is transmit.

    The block should be placed right before the audio sink where signal is transmitted to transciever.

    The block works as follow:
    * During initialization it opens serial port and sets RTS signal to Low ("RX")
    * When it gets any samples on input it:
        * swiches RTS signal to High ("TX")
        * optionally waits predelay interval to propagate start of transmission to Transciever
        * calculates time that the whole buffer will take to transmitt
        * copies input to output (it is done to ensure the audio sink will be placed after this block so any COM delay will be less risk) 
        * adds delay to that time and creates timer that will shut off TX state.
    * When another batch of samples would arive, the existing timer is cancelled and there is created new timer. This is done to ensure no break during transmission occur.
    * When timer wakes up, the RTS line is switched to False, that stops TX mode
    """
    def __init__(self, device, samp_rate, delay, predelay, is_predelay_used):
        gr.sync_block.__init__(self,
            name="pwsat2_ptt",
            in_sig=[numpy.float32],
            out_sig=[numpy.float32])

        self.ptt = serial.Serial()
        self.device = device
        self.samp_rate = samp_rate
        self.delay = delay
        self.predelay = predelay
        self.timer = None
        self.is_predelay_used = is_predelay_used
        self.is_predelay_fired = False

    def start(self):
        try:
            self.ptt.rts = False
            self.ptt.port = self.device
            self.ptt.open()
            self.is_predelay_fired = False
            return True 
        except:
            return False
        
    def stop(self):
        self.ptt.close()
        return True

    def stop_tx(self):
        self.ptt.rts = False
        self.is_predelay_fired = False

    def work(self, input_items, output_items):
        self.ptt.rts = True
        if self.timer:
            self.timer.cancel()

        in0 = input_items[0]
        out = output_items[0]

        length = len(in0)
        time_of_packet = float(length) / float(self.samp_rate)
        total_time = time_of_packet + self.delay

        out[:] = in0

        if self.is_predelay_used and not self.is_predelay_fired:
            sleep(self.predelay)
            self.is_predelay_fired = True

        self.timer = Timer(total_time, self.stop_tx)
        self.timer.start()

        return len(output_items[0])

