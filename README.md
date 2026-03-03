# DCC_Control
A project that controls a DCC model train set.
## Python Source for the Pico
dcc_driver.py       DCC driver class
console_main.py     Control program with console interface
auto_main.py        Control program to run a schedule
random_main.py      Control program to run a random route
schedule_2.py       A schedule for two trains
main.py             Main program
## Python Source for the PC Control Program
dcc_control.py      Simple GUI control program for my train set
dcc_frame.py        A Tkinter frame for each engine
tracks.py           Creates an image of the tracks
msg_box.py          Handles serial communication with the Pico
## KiCad PCB Files
Rev2.kicad_pro      Project file
Rev2.kicad_sch      PCB schematic
Rev2.kicad_pcb      PCB design
parts_list.txt      Parts list
## Sources for the DCC_Monitor application
dcc_monitor_main.py DCC monitor main program  
dcc_capture.py      DCC monitor PIO program
mon_schematic.png   DCC monitor schematic
