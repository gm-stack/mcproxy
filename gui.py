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
		gui = serverprops.gui
		
		#self.resize(250, 150)
		self.setWindowTitle('mcproxy')
		#self.statusBar().showMessage('Waiting for connection')
		#serverprops.guistatus['statusbar'] = self.statusBar()
		
		grid = QtGui.QGridLayout()
		grid.setSpacing(10)
		
		grid.addWidget(QtGui.QLabel('Current Time'), 1, 0)
		grid.addWidget(QtGui.QLabel('Current Position'), 2, 0)
		grid.addWidget(QtGui.QLabel('Player Angle'), 3, 0)
		
		gui['time'] = QtGui.QLabel('')
		gui['pos'] = QtGui.QLabel('X:\nY:\nZ:\n')
		gui['angle'] = QtGui.QLabel('Rotation:\nPitch:\nDirection:')
		
		grid.addWidget(gui['time'], 1, 1)
		grid.addWidget(gui['pos'], 2, 1)
		grid.addWidget(gui['angle'], 3, 1)
		
		grid.addWidget(QtGui.QLabel('Waypoint:'), 5, 0)
		
		gui['wplist'] = QtGui.QListWidget()
		
		QtCore.QObject.connect(gui['wplist'], QtCore.SIGNAL("currentItemChanged (QListWidgetItem *,QListWidgetItem *)"), self.wayPointSelected)
		grid.addWidget(gui['wplist'], 6, 0, 1, 2)
		
		gui['wpname'] = QtGui.QLabel('')
		gui['wploc'] = QtGui.QLabel('')
		gui['wpdir'] = QtGui.QLabel('')
		
		grid.addWidget(gui['wpname'], 7, 0, 1, 2)
		grid.addWidget(gui['wploc'], 8, 0, 1, 2)
		grid.addWidget(gui['wpdir'], 9, 0, 1, 2)
		
		gui['newwp'] = QtGui.QPushButton('New Waypoint')
		gui['wpnamef'] = QtGui.QLineEdit()
		
		grid.addWidget(gui['wpnamef'],10,0)
		grid.addWidget(gui['newwp'],10,1)
		QtCore.QObject.connect(gui['newwp'], QtCore.SIGNAL("clicked()"), self.newWayPoint)
		
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
	
	def newWayPoint(self):
		wpname = str(self.serverprops.gui['wpnamef'].text())
		if wpname:
			if not wpname in self.serverprops.waypoint:
				self.serverprops.gui['wplist'].addItem(wpname)
			self.serverprops.waypoint[wpname] = self.serverprops.playerdata['location']
			
			print "new waypoint %s" % wpname
