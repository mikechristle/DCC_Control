# ----------------------------------------------------------------------
# DCC Controller Console Interface Main
# MIT Licence 2025 Mike Christle
# ----------------------------------------------------------------------

from time import sleep, sleep_ms
from dcc_driver import DCC_Driver
from switch_driver import SwitchDriver
from machine import Pin
from utime import ticks_ms, ticks_diff

import gpio_numbers_R2 as gn

# Turnout Pulse LO for 250mSec
SWITCH_DELAY_MS = 250

driver = DCC_Driver(0, gn.D0A)
enable = Pin(gn.ENABLE, Pin.OUT, value=0)
switch = SwitchDriver(4, gn.D2A)
switch.start()

sense0 = Pin(gn.S0, Pin.IN)
sense1 = Pin(gn.S1, Pin.IN)
sense2 = Pin(gn.S2, Pin.IN)
sense3 = Pin(gn.S3, Pin.IN)
sensors = (sense0, sense1, sense2, sense3)
sense_times = [0, 0, 0, 0]

messages = {}

MENU = (
    "\nDCC Controller\n"
    "p0     - Stop sending messages\n"
    "p1     - Start sending messages\n"
    "ae e   - Add Engine with address e\n"
    "sp e n - Set speed for engine e to n percent\n"
    "tf e n - Toggle function bit n for engine e\n"
    "sw n s - Set switch n to straight\n"
    "sw n t - Set switch n to turn\n"
    "clear  - Remove all messages\n"
    )


# ----------------------------------------------------------------------
def set_switch(cmd):
    """sw n s - Set switch n to state s or t"""

    if len(cmd) != 3:
        print('Error: Invalid switch command. sw n (s or t).')
        return

    try:
        n = int(cmd[1]) * 2
    except:
        print('Error: Invalid switch command. sw n (s or t).')
        return

    if n < 0 or n > 7:
        print('Error: Invalid switch number, 0 -> 3.')
        return

    if cmd[2] not in ('s', 't'):
        print('Error: Invalid switch command. sw n (s or t).')
        return

    if cmd[2] == 't':
        n += 1

    print('Switch', n)
    switch.set_switch(n)


# ----------------------------------------------------------------------
def set_speed(cmd):
    """sp e n - Set speed for engine e to n percent"""

    if len(cmd) != 3:
        print('Error: Set Speed syntax: sp e n')
        return

    try:
        engine = int(cmd[1])
        speed = int(cmd[2])
    except:
        print('Error: Set Speed syntax: sp e n')
        return

    if engine not in messages:
        print('Error: Invalid engine number')
        return

    if -100 <= speed <= 100:
        msg = messages[engine][0]
        idx = messages[engine][1]

        if speed >= 0:
            msg[2] = (speed * 127 // 100) | 0x80
        else:
            msg[2] = speed * -127 // 100

        driver.update_message(idx, msg)
        print(f'Speed for engine {engine} set to {speed} percent.')

    else:
        print('speed out of range. -100 -> +100 percent.')


# ----------------------------------------------------------------------
def set_func(cmd):
    """tf e n - Toggle function bit n for engine e"""

    if len(cmd) != 3:
        print('Error: Toggle Function syntax: tf e n')
        return

    engine = int(cmd[1])
    if engine not in messages:
        print('Error: Invalid engine number')
        return

    func = int(cmd[2])
    if 1 <= func <= 4:
        msg = messages[engine][2]
        idx = messages[engine][3]
        val = 1 << (func - 1)
        msg[1] ^= val
        driver.update_message(idx, msg)
        print(f'Toggle F{func} for engine {engine}.')

    elif 5 <= func <= 8:
        msg = messages[engine][4]
        idx = messages[engine][5]
        val = 1 << (func - 5)
        msg[1] ^= val
        driver.update_message(idx, msg)
        print(f'Toggle F{func} for engine {engine}.')

    else:
        print('Func number out of range, 1 -> 8.')


# ----------------------------------------------------------------------
# speed_msg = [0x04, 0x3F, 0x80]
# f1234_msg = [0x04, 0x80]
# f5678_msg = [0x04, 0xB0]
# f9_12_msg = [0x04, 0xA0]
# f13_20_msg = [0x04, 0xDE, 0x00]
# f21_28_msg = [0x04, 0xDF, 0x00]
# ----------------------------------------------------------------------
def add_engine(cmd):
    """ae e - Add Engine with address e"""

    if len(cmd) != 2:
        print('Error: Add Engine syntax: ae e')
        return

    try:
        engine = int(cmd[1])
    except:
        print('Error: Add Engine syntax: ae e')
        return

    if engine < 1 or engine > 127:
        print('Error: Add Engine number out of range, 1 -> 127.')
        return

    speed_msg = [engine, 0x3F, 0x80]
    speed_idx = driver.add_message(speed_msg)

    f1234_msg = [engine, 0x80]
    f1234_idx = driver.add_message(f1234_msg)

    f5678_msg = [engine, 0xB0]
    f5678_idx = driver.add_message(f5678_msg)

    messages[engine] = (speed_msg, speed_idx,
                        f1234_msg, f1234_idx,
                        f5678_msg, f5678_idx)
    print(f'Engine {engine} added.')


# ----------------------------------------------------------------------
def sensor(pin):
    print('Interrupt', pin)
    sense_no = sensors.index(pin)
    itime = ticks_ms()
    otime = sense_times[sense_no]
    dtime = ticks_diff(itime, otime)
    if dtime > 1000:
        print('Valid interrupt:', sense_no, dtime / 1000)
        sense_times[sense_no] = itime


# ----------------------------------------------------------------------
def main():

    print('CONSOLE MAIN')

    sense0.irq(trigger=Pin.IRQ_FALLING, handler=sensor)
    sense1.irq(trigger=Pin.IRQ_FALLING, handler=sensor)
    sense2.irq(trigger=Pin.IRQ_FALLING, handler=sensor)
    sense3.irq(trigger=Pin.IRQ_FALLING, handler=sensor)

    add_engine(('ae','4'))
    add_engine(('ae','5'))

    while True:
        cmd = input().split()
        if len(cmd) == 0:
            print(MENU)

        elif cmd[0] == 'p0':
            enable.low()
            driver.stop()

        elif cmd[0] == 'p1':
            driver.start()
            enable.high()

        elif cmd[0] == 'ae':
            add_engine(cmd)

        elif cmd[0] == 'sp':
            set_speed(cmd)

        elif cmd[0] == 'tf':
            set_func(cmd)

        elif cmd[0] == 'sw':
            set_switch(cmd)

        elif cmd[0] == 'clear':
            driver.clear()


if __name__ == '__main__':
    main()
