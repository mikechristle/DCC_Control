# ---------------------------------------------------------------------------
# DCC Train Control Message Box
# Mike Christle 2025
# ---------------------------------------------------------------------------

import tkinter as tk


class MSG_Box:
    def __init__(self, root, port):
        self.root = root
        self.port = port

        self.box = tk.Text(root,
                           width=40, height=14,
                           bd=5, relief='sunken',
                           font='ARIAL 12',
                          )
        self.read_com_port()

    def write(self, cmnd):
        self.port.write((cmnd + '\r').encode('ascii'))

    def read_com_port(self):
        cnt = self.port.in_waiting
        if cnt > 0:
            data = self.port.read_all().decode(encoding="utf-8", errors="strict")
            self.box.insert(tk.END, data)

            lines = int(self.box.index("end-1c").split('.')[0])
            while lines > 14:
                self.box.delete('1.0', '2.0')
                lines -= 1

        self.root.after(500, self.read_com_port)
