import sys
import time
from Tkinter import *

framerate = 30

def start_gui(serverprops):
	root = Tk()
	
	serverprops.guistatus['time'] = StringVar("time")
	serverprops.guistatus['location'] = StringVar()
	serverprops.guistatus['angle'] = StringVar()
	serverprops.guistatus['humanreadable'] = StringVar()	
	
	Label(root, textvariable=serverprops.guistatus['time'], justify=LEFT).pack()
	Label(root, textvariable=serverprops.guistatus['location'], justify=LEFT).pack()
	Label(root, textvariable=serverprops.guistatus['angle'], justify=LEFT).pack()
	Label(root, textvariable=serverprops.guistatus['humanreadable'], justify=LEFT).pack()
	
	root.mainloop()

def input(event):
	print("got an event")
	return
