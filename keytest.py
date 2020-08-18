import pygame, os, sys
from pygame.locals import *
import datetime

pygame.init()
fpsClock = pygame.time.Clock()
#surface = pygame.display.set_mode((640, 480))
time_elapsed = 0
time = str(datetime.timedelta(seconds=time_elapsed))
pygame.display.set_mode((600, 400))

while True:
	keys = pygame.key.get_pressed()
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			print(format(pygame.key.get_mods(), 'b'))

# =============================================================================
# 			print(event.scancode, event.key, time, pygame.key.name(event.key))
# 		if event.type == KEYUP:
# 			print(event.scancode, event.key, time)
# 
# =============================================================================

	time_elapsed += fpsClock.get_time()
	time = str(datetime.timedelta(milliseconds=time_elapsed))
	fpsClock.tick(60)