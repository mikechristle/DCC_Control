# ----------------------------------------------------------------------
# DCC Monitor Main
# MIT Licence 2025 Mike Christle
# ----------------------------------------------------------------------

from time import sleep, ticks_ms
from dcc_capture import DCC_Capture


# ----------------------------------------------------------------------
def callback(data):
    """
    Called by the DCC_Capture class when a message is recieved.
    data    A tuple with the timestamp and a bytearray of data.
    """

    # Continue if address matches filter address, else abort
    if filter_adrs >= 0 and filter_adrs != data[1][0]:
        return

    # Print timestamp in seconds with accurace of milliseconds
    print(f'{data[0] / 1000.0:>8.3f}', end='')

    # Print data bytes and calculate checksum
    cs = 0
    for val in data[1]:
        print(f' {val:02X}', end='')
        cs ^= val

    # Validate the checksum
    if cs == 0:
        print('  OK')
    else:
        print('  ERROR')


# ----------------------------------------------------------------------
filter_adrs = -1
cap = DCC_Capture(0, 16, callback)
MENU = ('\nDCC Monitor\n'
        '1 - Start Monitor\n'
        '0 - Stop Monitor\n'
        'a - Set Filter Address\n'
        'c - Clear Filter Address\n'
        'x - Exit\n')

while True:
    cmd = input('> ')
    if len(cmd) == 0:
        print(MENU)

    elif cmd == 'x':
        if cap.active():
            cap.stop()
        break

    elif cmd[0] == '0':
        if cap.active():
            cap.stop()

    elif cmd[0] == '1':
        if not cap.active():
            cap.start()

    elif cmd[0] == 'a':
        if len(cmd) > 1:
            try:
                filter_adrs = int(cmd[1:])
                print('Filter address =', filter_adrs)
            except:
                filter_adrs = -1
                print('Invalid integer string')

    elif cmd[0] == 'c':
        filter_adrs = -1
        print('Filter address cleared')
