import sys
import pygame
import time

framerate = 30
font = None

def start_gui(serverprops):
	pygame.init()
	size = width, height = 640, 480
	serverprops.screen = pygame.display.set_mode(size)
	font = pygame.font.Font(None,12)
	

def pygame_event_loop(serverprops):
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: sys.exit()
		
		black = 0, 0, 0
		serverprops.screen.fill(black)
		text = font.render("x: %f, y: %f, z: %f" % serverprops.playerdata['location'], True, (255,255,255), (0,0,0))
		textRect = text.getRect()
		
		textRect.centerx = screen.get_rect().centerx
		textRect.centery = screen.get_rect().centery
		
		screen.blit(text, textRect)
		
		pygame.display.flip()

def input(event):
	print("got an event")
	return
