# ----------------------------------------------------------------------
# DCC Test Signal Driver
# MIT Licence 2025 Mike Christle
# ----------------------------------------------------------------------

from machine import Pin, Timer
from array import array
from time import sleep

import rp2


class DCC_Driver:

    # ----------------------------------------------------------------------
    def __init__(self, smn, gpio):
        """
        sm      State Machine Number.
        gpio    GPIO number of first output pin.
                The next sequencial gpio is the low output pin.
        """

        self.smn = smn
        self.msgs = []
        self.idx = 0
        self.timer = Timer()
        self.pause = False

        self.pin0 = Pin(gpio,     mode=Pin.OUT)
        self.pin1 = Pin(gpio + 1, mode=Pin.OUT)
        self.pin2 = Pin(gpio + 2, mode=Pin.OUT)
        self.pin3 = Pin(gpio + 3, mode=Pin.OUT)
        self.sm = rp2.StateMachine(
            smn,
            self.dcc_gen,
            freq=500_000,
            set_base=self.pin0,
            )


    # ----------------------------------------------------------------------
    def start(self):
        """Start message generation."""

        self.sm.active(1)
        self.timer.init(period=12, callback=self.sender)
        print('DCC Driver State Machines Started')


    # ----------------------------------------------------------------------
    def stop(self):
        """Stop message generation."""

        self.timer.deinit()
        self.sm.active(0)
        self.sm = rp2.StateMachine(
            self.smn,
            self.dcc_gen,
            freq=500_000,
            set_base=self.pin0,
            )

        print('DCC Driver State Machines Stopped')


    # ----------------------------------------------------------------------
    def active(self):
        """Returns True if messages are being generated."""

        return self.sm.active()


    # ----------------------------------------------------------------------
    def sender(self, _):
        """This function is call by the Timer."""

        cnt = len(self.msgs)
        if self.pause or cnt == 0:
            return

        if cnt <= self.idx:
            self.idx = 0

        if self.msgs[self.idx] is not None:
            self.sm.put(self.msgs[self.idx], 16)

        self.idx += 1


    # ----------------------------------------------------------------------
    def add_message(self, msg):
        """
        Add a message to the output gueue.
        msg  - A list containing the message data.
               Do not leave room for the checksum.
        Returns the index of the message in the queue.
        """

        # Create a half word array.
        bfr = array('H', [0 for _ in range(len(msg) + 3)])

        # Add the preamble
        bfr[0] = 0x0780
        bfr[1] = 0xFF00

        # Find an empty slot
        cnt = len(self.msgs)
        for idx in range(cnt):
            if self.msgs[idx] is None:
                self.msgs[idx] = bfr
                break

        # Else add to end of list
        else:
            self.msgs.append(bfr)
            idx = len(self.msgs) - 1

        # Add data to buffer
        self.update_message(idx, msg)
        return idx


    # ----------------------------------------------------------------------
    def update_message(self, idx, msg):
        """
        Replace the message in the queue with a new message.
        idx  - Index of the message in the queue.
        msg  - A list containing the message data.
               Do not leave room for the checksum.
        """

        # Ignore invalid indices and removed messages
        if idx >= len(self.msgs) or self.msgs[idx] is None:
            return

        # Add message data and calculate checksum
        checksum = 0
        for i in range(len(msg)):
            val = msg[i]
            self.msgs[idx][i + 2] = val << 8
            checksum ^= val

        # Add the checksum with end of message flag
        self.msgs[idx][i + 3] = (checksum << 8) | 0x80


    # ----------------------------------------------------------------------
    def remove_message(self, idx):
        """
        Remove a message from the message queue.
        idx  - Index of the message in the queue.
        """
        self.msgs[idx] = None


    # ----------------------------------------------------------------------
    def clear(self):
        """
        Clear all messages in the queue.
        """
        self.msgs.clear()


    # ----------------------------------------------------------------------
    # PIO Program
    # ----------------------------------------------------------------------
    @rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,
                           rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),
                           fifo_join=rp2.PIO.JOIN_TX) 
    def dcc_gen():

        label('lbl0')
        set(x, 0)
        set(y, 8)

        # Pull a word from the fifo
        # If fifo is empty, use the zero from x register
        pull(noblock)

        # Move MSB to the x register
        label('lbl1')
        out(x, 1)

        # Drive the DCC signal low
        set(pins, 10)

        # Test the bit in the x register
        jmp(not_x, 'lbl2')

        # Delay for a zero bit, then drive signal high
        nop() [26]
        set(pins, 5) [26]

        # Test and decrement bit counter
        jmp(y_dec, 'lbl1')
        jmp('lbl0')

        # Delay for a one bit, then drive signal high
        label('lbl2')
        nop() [20]
        nop() [26]
        set(pins, 5) [20]
        nop() [26]

        # Test and decrement bit counter
        jmp(y_dec, 'lbl1')
        jmp('lbl0')


# ----------------------------------------------------------------------
if __name__ == "__main__":

    gen = DCC_Driver(0, 0)
    gen.start()
    gen.add_message((1, 2, 4, 8, 16, 32, 64, 128, 0x55, 0xAA))
    sleep(1)
#    gen.stop()
#    print('Done')
