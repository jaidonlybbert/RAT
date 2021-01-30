# RAT - Robotic Analyzer of Tubes
# Copyright (C) 2021 Jaidon Lybbert

# Credit to:
# Pete Shinners - https://www.pygame.org/docs/tut/PygameIntro.html
# Radames Ajna - https://github.com/radames/opencv_video_to_pygame

"""This file and affiliate code in this directory serves to create a desktop GUI for recieving and sending data and control signals to the RAT device"""

import numpy as np
import pygame as pg
import cv2 as cv
import sys

pg.init()
# Robotic Analyzer of Tubes' Human Machine Interface Screen
pg.display.set_caption("RATHMIS")
size = width, height = 640, 480
screen = pg.display.set_mode(size)

camera = cv.VideoCapture(0)

while 1:
    
    ret, frame = camera.read()

    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    print("Width: ", camera.get(3))
    print("Height: ",  camera.get(4))
    print(frame.shape)
    print("Screen wxh: ", screen.get_size())
    frame = frame.swapaxes(0, 1)
    pg.surfarray.blit_array(screen, frame)
    pg.display.update()

    for event in pg.event.get():
        if event.type == pg.QUIT: 
            sys.exit()

