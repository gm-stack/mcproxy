import sys
import time
from PyQt4 import QtGui

framerate = 30

def start_gui(serverprops):
	app = QtGui.QApplication(sys.argv)
	main = MainWindow(serverprops)
	main.show()
	app.exec_()
	#root = Tk()
	
	#serverprops.guistatus['time'] = StringVar()
	#serverprops.guistatus['location'] = StringVar()
	#serverprops.guistatus['angle'] = StringVar()
	#serverprops.guistatus['humanreadable'] = StringVar()	
	
	#Label(root, textvariable=serverprops.guistatus['time'], justify=LEFT).pack()
	#Label(root, textvariable=serverprops.guistatus['location'], justify=LEFT).pack()
	#Label(root, textvariable=serverprops.guistatus['angle'], justify=LEFT).pack()
	#Label(root, textvariable=serverprops.guistatus['humanreadable'], justify=LEFT).pack()
	
	#root.mainloop()

class MainWindow(QtGui.QWidget):
	def __init__(self, serverprops):
		QtGui.QMainWindow.__init__(self)
		
		#self.resize(250, 150)
		self.setWindowTitle('mcproxy')
		#self.statusBar().showMessage('Waiting for connection')
		#serverprops.guistatus['statusbar'] = self.statusBar()
		
		grid = QtGui.QGridLayout()
		grid.setSpacing(10)
		
		grid.addWidget(QtGui.QLabel('Current Time'), 1, 0)
		grid.addWidget(QtGui.QLabel('Current Position'), 2, 0)
		grid.addWidget(QtGui.QLabel('Player Angle'), 3, 0)
		
		serverprops.gui['time'] = QtGui.QLabel('')
		serverprops.gui['pos'] = QtGui.QLabel('X:\nY:\nZ:\n')
		serverprops.gui['angle'] = QtGui.QLabel('Rotation:\nPitch:\nDirection:')
		
		grid.addWidget(serverprops.gui['time'], 1, 1)
		grid.addWidget(serverprops.gui['pos'], 2, 1)
		grid.addWidget(serverprops.gui['angle'], 3, 1)
		
		self.setLayout(grid)

def input(event):
	print("got an event")
	return
