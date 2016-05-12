import os, sys
import pygame
import pygame.transform

import smbus
import time
import math
from LSM9DS0 import *
import datetime
bus = smbus.SMBus(1)

import RPi.GPIO as GPIO
import time

import pyautogui

from game.registry import adjpos, adjrect, adjwidth, adjheight

# Game parameters
SCREEN_WIDTH, SCREEN_HEIGHT = adjpos (800, 500)
TITLE = "Symons Media: Duck Hunt"
FRAMES_PER_SEC = 50
BG_COLOR = 255, 255, 255

def writeACC(register,value):
        bus.write_byte_data(ACC_ADDRESS , register, value)
        return -1

def writeMAG(register,value):
        bus.write_byte_data(MAG_ADDRESS, register, value)
        return -1

def writeGRY(register,value):
        bus.write_byte_data(GYR_ADDRESS, register, value)
        return -1



def readACCx():
        acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_X_L_A)
        acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_X_H_A)
	acc_combined = (acc_l | acc_h <<8)

	return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readACCy():
        acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Y_L_A)
        acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Y_H_A)
	acc_combined = (acc_l | acc_h <<8)

	return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readACCz():
        acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Z_L_A)
        acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Z_H_A)
	acc_combined = (acc_l | acc_h <<8)

	return acc_combined  if acc_combined < 32768 else acc_combined - 65536


#initialise the accelerometer
writeACC(CTRL_REG1_XM, 0b01100111) #z,y,x axis enabled, continuos update,  100Hz data rate
writeACC(CTRL_REG2_XM, 0b00100000) #+/- 16G full scale


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
            oldx = readACCx()
            oldy = readACCy()
            for event in pygame.event.get():
                self.handleEvent(event)
            self.loop()
            self.render()
            newx = readACCx()
            newy = readACCy()
            if(oldx>newx):
            	pyautogui.moveRel(-10,0)
            elif(oldx<newx):
            	pyautogui.moveRel(10,0)
            if(oldy>newy):
            	pyautogui.moveRel(0,-10)
            elif(oldy<newy):
            	pyautogui.moveRel(0,10)
            
            if(GPIO.input(buttonPin)):
                pyautogui.click()
        self.cleanup()

if __name__ == "__main__":
    theGame = Game()
    theGame.execute()
