# ---------------------------------------------------------------------------
# DCC Train Controller
# Mike Christle 2025
# ---------------------------------------------------------------------------

import tkinter as tk

from dcc_frame import DCC_Frame
from serial import Serial
from tracks import Tracks
from msg_box import MSG_Box

COM_PORT = 'COM3'
port = Serial(COM_PORT)

root = tk.Tk()
root.title('DCC Train Controller')

# ---------------------------------------------------------------------------
msg_box = MSG_Box(root, port)
msg_box.box.grid(column=0, row=1)
msg_box.write('clear')

train4 = DCC_Frame(root, 'Passenger 3012', 4, msg_box)
train4.frame.grid(column=0, row=0)

train5 = DCC_Frame(root, 'Freight 3013', 5, msg_box)
train5.frame.grid(column=1, row=0)

tracks = Tracks(root, msg_box)
tracks.canvas.grid(column=1, row=1)

msg_box.write('sw 0 t')
msg_box.write('sw 1 t')
msg_box.write('sw 2 s')
msg_box.write('sw 3 s')

msg_box.write('p1')
root.mainloop()
msg_box.write('p0')
