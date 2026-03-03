# ----------------------------------------------------------------------
# DCC Signal Capture
# MIT Licence 2025 Mike Christle
# ----------------------------------------------------------------------

from machine import Pin
from time import sleep, ticks_ms
from micropython import schedule

import rp2


class DCC_Capture:

    def __init__(self, sm, gpio, func):
        """
        sm      State Machine number, 0-7.
        gpio    GPIO number of input pin.
        func    Callback function.
                Accepts two parameters in a single tuple.
                0 Time stamp in milliseconds.
                1 A bytearray of data.
        """

        self.func = func
        self.gpio = gpio
        self.dcc_signal = Pin(gpio, mode=Pin.IN)
        self.start_time = ticks_ms()

        self.sm = rp2.StateMachine(sm)
        self.sm.init(self.dcc_mon,
                     freq=200_000,
                     jmp_pin=self.dcc_signal,
                     in_base=self.dcc_signal,
                     )
        self.sm.irq(self.int_handler)

        self.FIFO_SIZE = 256
        SM_FIFO_ADRS = (0x50200020, 0x50200024, 0x50200028, 0x5020002C,
                        0x50300020, 0x50300024, 0x50300028, 0x5030002C)
        TREQ_SEL = (4, 5, 6, 7, 12, 13, 14, 15)

        self.fifo = bytearray(self.FIFO_SIZE)
        self.dma = rp2.DMA()
        self.ctrl = self.dma.pack_ctrl(
            size=0,  # BYTE
            inc_write=True,
            inc_read=False,
            treq_sel=TREQ_SEL[sm],
            )
        self.dma.config(
            read=SM_FIFO_ADRS[sm],
            write=self.fifo,
            count=self.FIFO_SIZE,
            ctrl=self.ctrl,
            )


    # ----------------------------------------------------------------------
    def start(self):
        """Starts the capture of DCC messages."""

        self.dma.active(1)
        self.sm.active(1)
        print('DCC Capture State Machines Started')


    # ----------------------------------------------------------------------
    def stop(self):
        """Stops the capture of DCC messages."""

        self.sm.active(0)
        self.dma.active(0)
        print('DCC Capture State Machines Stopped')


    # ----------------------------------------------------------------------
    def active(self):
        """Returns True if the capture is running."""

        return self.sm.active() or self.dma.active()


    # ----------------------------------------------------------------------
    def int_handler(self, sm):
        """
        Triggered by the PIO interrupt
        at the completion of each message.
        """

        time_stamp = ticks_ms() - self.start_time
        count = 256 - self.dma.count
        self.dma.active(0)
        bfr = self.fifo[:count]
        self.dma.count = self.FIFO_SIZE
        self.dma.write = self.fifo
        self.dma.active(1)
        schedule(self.func, (time_stamp, bfr))


    # ----------------------------------------------------------------------
    # The PIO program
    # ----------------------------------------------------------------------
    @rp2.asm_pio(fifo_join=rp2.PIO.JOIN_RX)
    def dcc_mon():

        # Wait for a one
        label('lbl0')
        wait(1, pin, 0)
        wait(0, pin, 0) [16]

        # If this is a one, start Preamble check
        jmp(pin, 'lbl1')

        # Else keep waiting
        jmp('lbl0')

        # Preamble check
        # Wait for at least 9 more ones
        label('lbl1')
        set(x, 9)

        label('lbl2')
        wait(1, pin, 0)
        wait(0, pin, 0) [16]

        # If a one, check the count
        jmp(pin, 'lbl3')

        # If less than 10 ones, start over
        jmp('lbl0')

        # If count < 9, continue preamble check
        label('lbl3')
        jmp(x_dec, 'lbl2')

        # Found a valid preamble, Wait for next zero
        label('lbl4')
        wait(1, pin, 0)
        wait(0, pin, 0) [16]
        jmp(pin, 'lbl4')

        # Input 8 data bits
        label('lbl5')
        set(x, 7)

        label('lbl6')
        wait(1, pin, 0)
        wait(0, pin, 0) [16]
        in_(pins, 1)
        jmp(x_dec, 'lbl6')

        # Save data byte to FIFO
        push()

        # Check acknowledge bit
        wait(1, pin, 0)
        wait(0, pin, 0) [16]

        # A one marks the end of message
        jmp(pin, 'lbl7')

        # On a zero, continue with next data byte
        jmp('lbl5')

        # End of message, send IRQ to software
        label('lbl7')
        irq(rel(0))
        jmp('lbl0')
