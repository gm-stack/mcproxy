import sys
import time
import positioning
from PyQt4 import QtGui, QtCore

framerate = 30

def start_gui(serverprops):
	app = QtGui.QApplication(sys.argv)
	main = MainWindow(serverprops)
	main.show()
	app.exec_()
	
def playerDataUpdate(serverprops):
	if serverprops.currentwp:
		playerpos = serverprops.playerdata['location']
		wppos = serverprops.waypoint[serverprops.currentwp]
		
		offset = positioning.getOffset(playerpos,wppos)
		angle = positioning.compassDirection(playerpos,wppos)
		hrangle = positioning.humanReadableAngle(angle)
		distance = positioning.getDistance2D(playerpos,wppos)
		serverprops.gui['wpdir'].setText("%.2f blocks %s\noffset: %i,%i,%i\nangle: %i" % (distance,hrangle,offset[0],offset[1],offset[2],angle))

class MainWindow(QtGui.QWidget):
	serverprops = None
	def __init__(self, serverprops):
		QtGui.QMainWindow.__init__(self)
		self.serverprops = serverprops
		
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
		
		grid.addWidget(QtGui.QLabel('Waypoint:'), 5, 0)
		
		serverprops.gui['wplist'] = QtGui.QListWidget()
		
		QtCore.QObject.connect(serverprops.gui['wplist'], QtCore.SIGNAL("currentItemChanged (QListWidgetItem *,QListWidgetItem *)"), self.wayPointSelected)
		grid.addWidget(serverprops.gui['wplist'], 6, 0, 1, 2)
		
		serverprops.gui['wpname'] = QtGui.QLabel('')
		serverprops.gui['wploc'] = QtGui.QLabel('')
		serverprops.gui['wpdir'] = QtGui.QLabel('')
		
		grid.addWidget(serverprops.gui['wpname'], 7, 0, 1, 2)
		grid.addWidget(serverprops.gui['wploc'], 8, 0, 1, 2)
		grid.addWidget(serverprops.gui['wpdir'], 9, 0, 1, 2)
		
		
		self.setLayout(grid)
	
	def wayPointSelected(self, current=None, previous=None):
		selwp = str(current.text())
		self.serverprops.currentwp = selwp
		print "selected waypoint: %s" % selwp
		self.serverprops.gui['wpname'].setText(selwp)
		print self.serverprops.waypoint
		if selwp in self.serverprops.waypoint:
			self.serverprops.gui['wploc'].setText("%.2f,%.2f,%.2f" % self.serverprops.waypoint[selwp])
		else:
			print "waypoint undefined"
			self.serverprops.gui['wploc'].setText("unknown")
