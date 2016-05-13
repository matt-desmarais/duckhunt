import os, sys
import pygame
import pygame.transform

import time
import datetime
import smbus
from BerryImu import BerryImu


import RPi.GPIO as GPIO
import time

import pyautogui

from game.registry import adjpos, adjrect, adjwidth, adjheight

# Game parameters
SCREEN_WIDTH, SCREEN_HEIGHT = adjpos (800, 500)
TITLE = "Symons Media: Duck Hunt"
FRAMES_PER_SEC = 50
BG_COLOR = 255, 255, 255


bus = smbus.SMBus(1)
imu = BerryImu(bus)
imu.initialise()


# Initialize pygame before importing modules
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()
pygame.display.set_caption(TITLE)
pygame.mouse.set_visible(False)

import game.driver

#adjust for where your switch is connected
buttonPin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonPin,GPIO.IN)

class Game(object):
    def __init__(self):
        self.running = True
        self.surface = None
        self.clock = pygame.time.Clock()
        self.size = SCREEN_WIDTH, SCREEN_HEIGHT
        background = os.path.join('media', 'background.jpg')
        bg = pygame.image.load(background)
        self.background = pygame.transform.smoothscale (bg, self.size)
        self.driver = None
	oldx = SCREEN_HEIGHT/2;
        oldy = SCREEN_WIDTH/2;
	
    def init(self):
        self.surface = pygame.display.set_mode(self.size)
        self.driver = game.driver.Driver(self.surface)

    def handleEvent(self, event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key is 27):
            self.running = False
        else:
            self.driver.handleEvent(event)

    def loop(self):
        self.clock.tick(FRAMES_PER_SEC)
        self.driver.update()

    def render(self):
        self.surface.blit(self.background, (0,0))
        self.driver.render()
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()
        sys.exit(0)

    def execute(self):
        self.init()

        while (self.running):
	    acc_meas = imu.read_acc_data()
	    gyr_meas = imu.read_gyr_data()
	    mag_meas = imu.read_mag_data()

	    # Flip acceleration to match Raspberry Pi frame (rotate around Y_ACC)
	    acc_meas[2] = -acc_meas[2]
	    acc_meas[0] = -acc_meas[0]


            for event in pygame.event.get():
                self.handleEvent(event)
            self.loop()
            self.render()
      	    pyautogui.moveRel(mag_meas[1], 0)
            
            if(GPIO.input(buttonPin)):
                pyautogui.click()
        self.cleanup()

if __name__ == "__main__":
    theGame = Game()
    theGame.execute()
