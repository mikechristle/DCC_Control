# ---------------------------------------------------------------------------
# DCC Train Control Track Display
# Mike Christle 2025
# ---------------------------------------------------------------------------

import tkinter as tk
from PIL import Image, ImageTk

class Tracks:
    def __init__(self, root, port):
        self.root = root
        self.port = port

        self.canvas = tk.Canvas(self.root,
                                width=360, height=288,
                                bg='green')

        self.s0 = False
        self.s1 = False
        self.s2 = False
        self.s3 = False

        layout = ('DBBBBBBMBE',
                  'CADBBBBMBI',
                  'CAHBBBBEAC',
                  'CACAAAACAC',
                  'CACAAAACAC',
                  'CALBMBBFAC',
                  'CAGBMBBBBI',
                  'GBBBBBBBBF',
                  )

        self.images = []
        self.images.append(ImageTk.PhotoImage(Image.open('images/Blank.bmp')))      # A 0
        self.images.append(ImageTk.PhotoImage(Image.open('images/TrackH.bmp')))     # B 1
        self.images.append(ImageTk.PhotoImage(Image.open('images/TrackV.bmp')))     # C 2
        self.images.append(ImageTk.PhotoImage(Image.open('images/TrackDL.bmp')))    # D 3
        self.images.append(ImageTk.PhotoImage(Image.open('images/TrackDR.bmp')))    # E 4
        self.images.append(ImageTk.PhotoImage(Image.open('images/TrackUL.bmp')))    # F 5
        self.images.append(ImageTk.PhotoImage(Image.open('images/TrackUR.bmp')))    # G 6
        self.images.append(ImageTk.PhotoImage(Image.open('images/SwitchDL.bmp')))   # H 7
        self.images.append(ImageTk.PhotoImage(Image.open('images/SwitchV.bmp')))    # I 8
        self.images.append(ImageTk.PhotoImage(Image.open('images/SwitchDR.bmp')))   # J 9
        self.images.append(ImageTk.PhotoImage(Image.open('images/SwitchUL.bmp')))   # K 10
        self.images.append(ImageTk.PhotoImage(Image.open('images/SwitchUR.bmp')))   # L 11
        self.images.append(ImageTk.PhotoImage(Image.open('images/Sensor.bmp')))     # M 12

        for y in range(8):
            for x in range(10):
                char = ord(layout[y][x]) - 65
                print(layout[y][x], char)
                self.canvas.create_image(x * 36, y * 36,
                                         image=self.images[char],
                                         anchor=tk.NW)
        self.canvas.bind('<Button-1>', self.click)


    def click(self, event):
        x = event.x // 36
        y = event.y // 36

        if x == 2:
            if y == 2:
                self.s0 = not self.s0
                if self.s0:
                    self.canvas.create_image(72, 72,
                                             image=self.images[8],
                                             anchor=tk.NW)
                    self.port.write('sw 0 s')
                else:
                    self.canvas.create_image(72, 72,
                                             image=self.images[7],
                                             anchor=tk.NW)
                    self.port.write('sw 0 t')
            elif y == 5:
                self.s1 = not self.s1
                if self.s1:
                    self.canvas.create_image(72, 180,
                                             image=self.images[8],
                                             anchor=tk.NW)
                    self.port.write('sw 1 S')
                else:
                    self.canvas.create_image(72, 180,
                                             image=self.images[11],
                                             anchor=tk.NW)
                    self.port.write('sw 1 T')
        elif x == 9:
            if y == 1:
                self.s2 = not self.s2
                if self.s2:
                    self.canvas.create_image(324, 36,
                                             image=self.images[9],
                                             anchor=tk.NW)
                    self.port.write('sw 2 t')
                else:
                    self.canvas.create_image(324, 36,
                                             image=self.images[8],
                                             anchor=tk.NW)
                    self.port.write('sw 2 s')
            elif y == 6:
                self.s3 = not self.s3
                if self.s3:
                    self.canvas.create_image(324, 216,
                                             image=self.images[10],
                                             anchor=tk.NW)
                    self.port.write('sw 3 t')
                else:
                    self.canvas.create_image(324, 216,
                                             image=self.images[8],
                                             anchor=tk.NW)
                    self.port.write('sw 3 s')
