# ----------------------------------------------------------------------
# DCC Controller Random Path Main
# MIT Licence 2025 Mike Christle
# ----------------------------------------------------------------------

from uasyncio import sleep_ms, create_task, run
from dcc_driver import DCC_Driver
from machine import Pin
from utime import ticks_ms, ticks_diff
from random import getrandbits
from switch_driver import SwitchDriver

import gpio_numbers_R2 as gn

# Turnout Pulse LO for 250mSec
SWITCH_DELAY_MS = 250

# Switch States
STRAIGHT = 0
TURN = 1

# Function Options
BELL = 1
HORN = 2

driver = DCC_Driver(0, gn.D0A)
switch = SwitchDriver(4, gn.D2A)
enable = Pin(gn.ENABLE, Pin.OUT, value=0)

sense0 = Pin(gn.S0, Pin.IN)
sense1 = Pin(gn.S1, Pin.IN)
sense2 = Pin(gn.S2, Pin.IN)
sense3 = Pin(gn.S3, Pin.IN)
sensors = (sense0, sense1, sense2, sense3)
sense_times = [ticks_ms(), ticks_ms(), ticks_ms(), ticks_ms()]

messages = {}
queue = []
engines = ([], [], [], [])
running = True


# ----------------------------------------------------------------------
async def set_switch(delay, sw_num, pos):
    """
             Set a switch.
    delay  - Time to wait before switch in mSec.
    sw_num - Switch to set, 0-3.
    pos    - 0 = Straight, 1 = Turn.
    """

    await sleep_ms(delay)
    print('set_switch', sw_num, pos)

    sw_num <<= 1
    if pos:
        sw_num += 1

    switch.set_switch(sw_num)
#     pin = SWITCHES[sw_num]
#     pin.low()
#     await sleep_ms(SWITCH_DELAY_MS)
#     pin.high()


# ----------------------------------------------------------------------
async def set_speed(delay, engine, speed):
    """
             Set the speed of an engine.
    delay  - Time to wait before settomg speed in mSec.
    engine - Engine number.
    speed  - Speed, 0-100 percent.
    """

    await sleep_ms(delay)
    print('set_speed', engine, speed)

    msg = messages[engine][0]
    idx = messages[engine][1]

    if speed >= 0:
        msg[2] = (speed * 127 // 100) | 0x80
    else:
        msg[2] = speed * -127 // 100

    driver.update_message(idx, msg)


# ----------------------------------------------------------------------
async def set_func(delay, engine, func):

    await sleep_ms(delay)
    print('set_func', engine, func)

    if 1 <= func <= 4:
        msg = messages[engine][2]
        idx = messages[engine][3]
        msg[1] |= (1 << (func - 1))

    elif 5 <= func <= 8:
        msg = messages[engine][4]
        idx = messages[engine][5]
        msg[1] |= (1 << (func - 5))

    driver.update_message(idx, msg)


# ----------------------------------------------------------------------
async def clr_func(delay, engine, func):

    await sleep_ms(delay)
    print('clr_func', engine, func)

    if 1 <= func <= 4:
        msg = messages[engine][2]
        idx = messages[engine][3]
        msg[1] &= ~(1 << (func - 1))
        driver.update_message(idx, msg)

    elif 5 <= func <= 8:
        msg = messages[engine][4]
        idx = messages[engine][5]
        msg[1] &= ~(1 << (func - 5))
        driver.update_message(idx, msg)


# ----------------------------------------------------------------------
async def event_loop():
   while running:
        while len(queue) > 0:
            func, p1, p2, p3 = queue.pop(0)
            create_task(func(p1, p2, p3))
        await sleep_ms(100)


# ----------------------------------------------------------------------
# speed_msg = [0x04, 0x3F, 0x80]
# f1234_msg = [0x04, 0x80]
# f5678_msg = [0x04, 0xB0]
# f9_12_msg = [0x04, 0xA0]
# f13_20_msg = [0x04, 0xDE, 0x00]
# f21_28_msg = [0x04, 0xDF, 0x00]
# ----------------------------------------------------------------------
def add_engine(engine):

    print(f'Add engine {engine}.')

    speed_msg = [engine, 0x3F, 0x80]
    speed_idx = driver.add_message(speed_msg)

    f1234_msg = [engine, 0x80]
    f1234_idx = driver.add_message(f1234_msg)

    f5678_msg = [engine, 0xB0]
    f5678_idx = driver.add_message(f5678_msg)

    messages[engine] = (speed_msg, speed_idx,
                        f1234_msg, f1234_idx,
                        f5678_msg, f5678_idx)


# ----------------------------------------------------------------------
def sensor_irq(pin):
    global running

    # Get the sensor number
    sensor_no = sensors.index(pin)

    # Check delay from last interrupt
    # Ignore if delay is too short
    itime = ticks_ms()
    dtime = sense_times[sensor_no]
    dtime = ticks_diff(itime, dtime)
    sense_times[sensor_no] = itime
    if dtime < 1000:
        return

    print('Interrupt:', sensor_no)

    # If no engine is expected abort
    if len(engines[sensor_no]) == 0:
        print('ERROR: Interrupt not expected.')
        running = False
        return

    # Get the engine number
    engine = engines[sensor_no].pop(0)

    # Pick a random path
    choice = bool(getrandbits(1))

    # Find min delay on both input paths
    delay = 0
    ntime = sense_times[sensor_no ^ 1]
    ntime = ticks_diff(itime, ntime)
    if min(dtime, ntime) < 3_000:
        print(dtime, ntime)

        # Delay the current engine
        delay = 5_000
        queue.append((set_speed, 0, engine, 0))
        queue.append((set_func, 0, engine, HORN))
        queue.append((clr_func, 2_000, engine, HORN))

    # Route the engine thru the first switch
    queue.append((set_speed, delay, engine, 40))
    queue.append((set_func, delay, engine, BELL))
    queue.append((clr_func, delay + 2_000, engine, BELL))

    # Route the engine thru the second switch
    if sensor_no < 2:
        if sensor_no == 0:
            queue.append((set_switch, delay, 1, STRAIGHT))
        else: # engine == 1
            queue.append((set_switch, delay, 1, TURN))

        if choice:
            queue.append((set_switch, delay, 0, STRAIGHT))
            queue.append((set_speed, delay + 8_000, engine, 50))
            engines[2].append(engine)
        else:
            queue.append((set_switch, delay, 0, TURN))
            queue.append((set_speed, delay + 8_000, engine, 50))
            engines[1].append(engine)

    else: # sensor_no >= 2
        if sensor_no == 2:
            queue.append((set_switch, delay, 2, TURN))
        else: # sensor_no == 3
            queue.append((set_switch, delay, 2, STRAIGHT))

        if choice:
            queue.append((set_switch, delay, 3, STRAIGHT))
            queue.append((set_speed, delay + 8_000, engine, 50))
            engines[3].append(engine)
        else:
            queue.append((set_switch, delay, 3, TURN))
            queue.append((set_speed, delay + 8_000, engine, 50))
            engines[0].append(engine)


# ----------------------------------------------------------------------
def main():

    sense0.irq(trigger=Pin.IRQ_FALLING, handler=sensor_irq)
    sense1.irq(trigger=Pin.IRQ_FALLING, handler=sensor_irq)
    sense2.irq(trigger=Pin.IRQ_FALLING, handler=sensor_irq)
    sense3.irq(trigger=Pin.IRQ_FALLING, handler=sensor_irq)

    add_engine(4)
    engines[1].append(4)
    queue.append((set_speed, 0, 4, 50))

    add_engine(5)
    engines[3].append(5)
    queue.append((set_speed, 0, 5, 50))

    switch.start()
    driver.start()
    enable.high()
    run(event_loop())


# ----------------------------------------------------------------------
if __name__ == '__main__':
    main()


