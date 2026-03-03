# ----------------------------------------------------------------------
# DCC Controller Auto Run Main
# MIT Licence 2025 Mike Christle
# ----------------------------------------------------------------------

from uasyncio import sleep_ms, create_task, run
from dcc_driver import DCC_Driver
from machine import Pin
from utime import ticks_ms, ticks_diff
from schedule_2 import event_sch
from switch_driver import SwitchDriver

import gpio_numbers_R2 as gn

# Turnout Pulse LO for 250mSec
SWITCH_DELAY_MS = 250

driver = DCC_Driver(0, gn.D0A)
enable = Pin(gn.ENABLE, Pin.OUT, value=0)
switch = SwitchDriver(4, gn.D2A)

sense0 = Pin(gn.S0, Pin.IN)
sense1 = Pin(gn.S1, Pin.IN)
sense2 = Pin(gn.S2, Pin.IN)
sense3 = Pin(gn.S3, Pin.IN)
sensors = (sense0, sense1, sense2, sense3)
sense_times = [0, 0, 0, 0]

messages = {}
queue = []
events = {}
states = {}


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

    # Calculate the pin number
    sw_num <<= 1
    if pos:
        sw_num += 1

    # Drive pin low for 250 mSec
    switch.set_switch(sw_num)


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

    # Get this engines speed message
    msg = messages[engine][0]
    idx = messages[engine][1]

    # Set the speed in the message
    if speed >= 0:
        msg[2] = (speed * 127 // 100) | 0x80
    else:
        msg[2] = speed * -127 // 100

    # Update the message
    driver.update_message(idx, msg)


# ----------------------------------------------------------------------
async def set_func(delay, engine, func):

    await sleep_ms(delay)
    print('set_func', engine, func)

    # Update the appropriate message
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

    # Wait so other tasks can run
    await sleep_ms(delay)
    print('clr_func', engine, func)

    # Update the appropriate message
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
FUNCS = set_switch, set_speed, set_func, clr_func

async def event_loop():
   while True:

        # If any tasks in the queue
        while len(queue) > 0:

            # Get and execute each task
            func, p1, p2, p3 = queue.pop(0)
            func = FUNCS[func]
            create_task(func(p1, p2, p3))

        # Delay so tasks can run
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

    # Create a speed message
    speed_msg = [engine, 0x3F, 0x80]
    speed_idx = driver.add_message(speed_msg)

    # Create message for F1 to F4
    f1234_msg = [engine, 0x80]
    f1234_idx = driver.add_message(f1234_msg)

    # Create message for F5 to F8
    f5678_msg = [engine, 0xB0]
    f5678_idx = driver.add_message(f5678_msg)

    # Add messages to message dictionary
    messages[engine] = (speed_msg, speed_idx,
                        f1234_msg, f1234_idx,
                        f5678_msg, f5678_idx)


# ----------------------------------------------------------------------
def sensor_irq(pin):
    print('Interrupt', pin)
    
    # Get the sensor number
    sensor_no = sensors.index(pin)

    # Ignore interrupts thet are too close in time
    itime = ticks_ms()
    otime = sense_times[sensor_no]
    dtime = ticks_diff(itime, otime)
    sense_times[sensor_no] = itime
    if dtime < 1000:
        return

    print('Valid interrupt:', sensor_no, dtime / 1000)

    # Find the correct state
    for engine, state in states.items():
        if sensor_no == (state & 15):

            # Schedule the actions
            actions = events[state]
            for action in actions[1]:
                queue.append(action)

            # Update the state number
            states[engine] = actions[0]


# ----------------------------------------------------------------------
def main():

    # Configure sonsor pins
    sense0.irq(trigger=Pin.IRQ_FALLING, handler=sensor_irq)
    sense1.irq(trigger=Pin.IRQ_FALLING, handler=sensor_irq)
    sense2.irq(trigger=Pin.IRQ_FALLING, handler=sensor_irq)
    sense3.irq(trigger=Pin.IRQ_FALLING, handler=sensor_irq)

    # For each state in the schedule add the actions
    for state, actions in event_sch:
        events[state] = actions

        # If this is the first state for this engine
        # add this engine and initialize to this state
        engine = state >> 12
        if engine not in states:
            add_engine(engine)
            states[engine] = actions[0]
            for action in actions[1]:
                queue.append(action)

    switch.start()      # Start the switch driver
    driver.start()      # Start the DCC driver
    enable.high()       # Set the driver ENABLE signal
    run(event_loop())   # Start event schedular


# ----------------------------------------------------------------------
if __name__ == '__main__':
    main()

