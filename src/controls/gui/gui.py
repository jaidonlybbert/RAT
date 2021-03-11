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


# Screen initialization 
pg.init()
pg.display.set_caption("RAT Human Machine Interface")
screen_size = width, height = 1280, 720 
screen = pg.display.set_mode(screen_size)

# Camera window creation
camera_window = pg.Surface((640, 480))
camera = cv.VideoCapture(0)

# 3D scan results viewer
scan = pg.image.load('scan_result.jpeg')
scan_window = pg.Surface((640, 480))


def newScan():
    global scan
    scan = pg.image.load('scan_result.jpeg')


def main():
    while 1:
        # Read a frame from the camera w/ openCV (read as numpy array)
        ret, frame = camera.read()
        # Convert default format to format read understood by pygame
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Debugging image format
        print("Width: ", camera.get(3))
        print("Height: ",  camera.get(4))
        print(frame.shape)
        print("Screen wxh: ", screen.get_size())
        # The height and width are swapped in OpenCV vs Pygame
        frame = frame.swapaxes(0, 1)
        
        # Draw camera feed onto the camera_window surface
        pg.surfarray.blit_array(camera_window, frame)
        # Draw camera_window onto screen surface
        screen.blit(camera_window, (0, 0))
        # Update display
        pg.display.update()

        # Draw 3D scan results
        screen.blit(scan, (640, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT: 
                sys.exit()


if __name__ == '__main__':
    main()
