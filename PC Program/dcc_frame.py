# ---------------------------------------------------------------------------
# DCC Train Control Frame
# Mike Christle 2025
# ---------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk


class DCC_Frame:
    font = 'arial 16'
    active_color = 'light green'  #'#008000'

    def __init__(self, parent, title, adrs, port):
        self.adrs = adrs
        self.port = port

        self.speed_val = tk.IntVar()
        self.speed_val.set(0)

        self.frame = tk.Frame(parent, bd=5, relief='sunken')

        self.title = tk.Label(self.frame,
                              text=title,
                              font=DCC_Frame.font)
        self.title.grid(column=0, row=0, columnspan=3, pady=10)

        self.btn_lights = tk.Button(self.frame,
                                    font=DCC_Frame.font,
                                    text='LIGHTS',
                                    width=10,
                                    command=self.btn_lights_cmnd)
        self.btn_lights.grid(column=0, row=1)

        self.btn_bell = tk.Button(self.frame,
                                  font=DCC_Frame.font,
                                  text='BELL',
                                  width=10,
                                  command=self.btn_bell_cmnd)
        self.btn_bell.grid(column=1, row=1)

        self.btn_horn = tk.Button(self.frame,
                                  font=DCC_Frame.font,
                                  text='AIR HORN',
                                  width=10,
                                  command=self.btn_horn_cmnd)
        self.btn_horn.grid(column=2, row=1)

        self.speed = ttk.Scale(self.frame,
                               from_=-20, to=+20,
                               orient=tk.HORIZONTAL,
                               variable=self.speed_val)
                               # command=self.speed_change)
        self.speed.grid(column=0, row=2, columnspan=2, sticky='ew')
        self.speed.bind("<ButtonRelease-1>", self.speed_change)
        self.speed.bind("<ButtonRelease-3>", self.speed_reset)

        self.speed_lbl = tk.Label(self.frame, text='0%', font=DCC_Frame.font)
        self.speed_lbl.grid(column=2, row=2)

        self.port.write(f'ae {self.adrs}')

    def speed_reset(self, _):
        self.speed_val.set(0)
        self.speed_change(0)

    def speed_change(self, _):
        text = f'{self.speed_val.get() * 5}%'
        self.speed_lbl.config(text=text)
        self.port.write(f'sp {self.adrs} {text[:-1]}')

    def btn_bell_cmnd(self):
        self.btn_cmnd(self.btn_bell, 1)

    def btn_horn_cmnd(self):
        self.btn_cmnd(self.btn_horn, 2)

    def btn_lights_cmnd(self):
        self.btn_cmnd(self.btn_lights, 3)

    def btn_cmnd(self, btn, fn):
        self.port.write(f'tf {self.adrs} {fn}')

        if btn.cget('bg') == 'SystemButtonFace':
            btn.config(bg=DCC_Frame.active_color)
        else:
            btn.config(bg='SystemButtonFace')

