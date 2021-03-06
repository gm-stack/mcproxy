import sys
import time
import positioning
import hooks
import mcpackets
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

def removeFromMenu(menu,item):
	num = menu.count()
	for i in range(num):
		itemname = str(menu.item(i).text())
		if itemname == item:
			menu.takeItem(i)
			break


class MainWindow(QtGui.QWidget):
	serverprops = None
	def __init__(self, serverprops):
		QtGui.QMainWindow.__init__(self)
		#self.serverprops = serverprops
		
		# start main window with gridlayout
		self.setWindowTitle('mcproxy')
		grid = QtGui.QGridLayout()
		grid.setSpacing(10)
		self.setLayout(grid)
		
# add player info
	#Anonymous labels
		grid.addWidget(QtGui.QLabel('Current Time'), 1, 0)
		grid.addWidget(QtGui.QLabel('Current Position'), 2, 0)
		grid.addWidget(QtGui.QLabel('Player Angle'), 3, 0)
	#named entities
		qlTime = QtGui.QLabel('') #gui['time']
		qlPosition = QtGui.QLabel('X:\nY:\nZ:\n') #gui['pos']
		qlAngle = QtGui.QLabel('Rotation:\nPitch:\nDirection:') #gui['angle']
	#layout entities
		grid.addWidget(qlTime, 1, 1)
		grid.addWidget(qlPosition, 2, 1)
		grid.addWidget(qlAngle, 3, 1)
		
# add waypoint list
	#Anonymous labels	
		grid.addWidget(QtGui.QLabel('Waypoint:'), 5, 0)
	#named entities
		qbWPDelete = QtGui.QPushButton('-') #gui['wpdel']
		qbSetCompass = QtGui.QPushButton('Set Compass') #gui['wpcomp']
		qbTeleport = QtGui.QPushButton('Teleport') #gui['wptele']
		qlWaypoints = QtGui.QListWidget() #gui['wplist']
	#layout entities
		qhbWPButtons = QtGui.QHBoxLayout()
		qhbWPButtons.addWidget(qbWPDelete)
		qhbWPButtons.addWidget(qbSetCompass)
		qhbWPButtons.addWidget(qbTeleport)
		grid.addLayout(qhbWPButtons,5,1)
		grid.addWidget(qlWaypoints, 6, 0, 1, 2)
	#connect signals
		QtCore.QObject.connect(qbSetCompass, QtCore.SIGNAL("clicked()"), self.compassWayPoint)
		QtCore.QObject.connect(qbTeleport, QtCore.SIGNAL("clicked()"), self.Teleport)
		QtCore.QObject.connect(qlWaypoints, QtCore.SIGNAL("currentItemChanged (QListWidgetItem *,QListWidgetItem *)"), self.wayPointSelected)

#Waypoint Information
	#Anonyamous labels
		qlWPName = QtGui.QLabel('') #gui['wpname']
		qlWPLocation = QtGui.QLabel('') #gui['wploc']
		qlWPDirection = QtGui.QLabel('') #gui['wpdir']
		
		qWP = QtGui.QPushButton('New Waypoint') #gui['newwp']
		gui['wpnamef'] = QtGui.QLineEdit()
		grid.addWidget(qlWPName, 7, 0, 1, 2)
		grid.addWidget(qlWPLocation, 8, 0, 1, 2)
		grid.addWidget(qlWPDirection, 9, 0, 1, 2)
		grid.addWidget(gui['wpnamef'],10,0)
		grid.addWidget(gui['newwp'],10,1)
		QtCore.QObject.connect(gui['newwp'], QtCore.SIGNAL("clicked()"), self.newWayPoint)
		gui['wpx'] = QtGui.QLineEdit()
		gui['wpy'] = QtGui.QLineEdit()
		gui['wpz'] = QtGui.QLineEdit()
		gui['wplocbtn'] = QtGui.QPushButton('New with loc')
		xyz = QtGui.QHBoxLayout()
		xyz.addWidget(gui['wpx'])
		xyz.addWidget(gui['wpy'])
		xyz.addWidget(gui['wpz'])
		xyz.addWidget(gui['wplocbtn'])
		QtCore.QObject.connect(gui['wplocbtn'], QtCore.SIGNAL("clicked()"), self.newWayPointWithLoc)
		gui['wpx'].setFixedWidth(40)
		gui['wpy'].setFixedWidth(40)
		gui['wpz'].setFixedWidth(40)
		grid.addLayout(xyz,11,0,1,2)
		
		# add hooks list
		hookgrid = QtGui.QGridLayout()
		hookgrid.addWidget(QtGui.QLabel("Hooks"),1,0,1,2)
		hookgrid.addWidget(QtGui.QLabel("Available"),2,0)
		hookgrid.addWidget(QtGui.QLabel("Active"),2,1)
		gui['hooklist'] = QtGui.QListWidget()
		gui['hookactive'] = QtGui.QListWidget()
		hooks.setupInitialHooks(self.serverprops)
		
		
		gui['hooklist'].setFixedWidth(130)
		gui['hookactive'].setFixedWidth(130)
		hookgrid.addWidget(gui['hooklist'],3,0,3,1)
		hookgrid.addWidget(gui['hookactive'],3,1,3,1)
		gui['activate'] = QtGui.QPushButton('Activate ->')
		gui['deactivate'] = QtGui.QPushButton('<- Remove')
		hookgrid.addWidget(gui['activate'],6,0)
		hookgrid.addWidget(gui['deactivate'],6,1)
		QtCore.QObject.connect(gui['activate'], QtCore.SIGNAL("clicked()"), self.activateHook)
		QtCore.QObject.connect(gui['deactivate'], QtCore.SIGNAL("clicked()"), self.deactivateHook)
		grid.addLayout(hookgrid,1,2,5,2)
		
	
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
			positioning.saveWaypoints(self.serverprops)
	
	def newWayPointWithLoc(self):
		wpname = str(self.serverprops.gui['wpnamef'].text())
		try:
			wpx = int(str(self.serverprops.gui['wpx'].text()))
			wpy = int(str(self.serverprops.gui['wpy'].text()))
			wpz = int(str(self.serverprops.gui['wpz'].text()))
		except:
			print "not an integer value"
			return
		if wpname:
			if not wpname in self.serverprops.waypoint:
				self.serverprops.gui['wplist'].addItem(wpname)
			self.serverprops.waypoint[wpname] = (wpx,wpy,wpz)
			positioning.saveWaypoints(self.serverprops)
	
	def removeWayPoint(self):
		pass
	
	def Teleport(self):
		wploc = self.serverprops.waypoint[self.serverprops.currentwp]
		packet = {'x':wploc[0], 'y':wploc[1]+5, 'stance':0, 'z':wploc[2], 'rotation':0, 'pitch':0, 'flying':0}
		encpacket = mcpackets.encode("s2c",mcpackets.name_to_id['playermovelook'],packet)
		self.serverprops.comms.clientqueue.put(encpacket)
		
	def compassWayPoint(self):
		wploc = self.serverprops.waypoint[self.serverprops.currentwp]
		packet = {'x':wploc[0], 'y':wploc[1], 'z':wploc[2]}
		encpacket = mcpackets.encode("s2c", mcpackets.name_to_id['spawnposition'], packet)
		self.serverprops.comms.clientqueue.put(encpacket)
	
	def activateHook(self):
		selected = str(self.serverprops.gui['hooklist'].currentItem().text())
		hooks.addHook(self.serverprops,selected)
	
	def deactivateHook(self):
		selected = str(self.serverprops.gui['hookactive'].currentItem().text())
		hooks.removeHook(self.serverprops,selected)