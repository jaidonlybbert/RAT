# RAT - Robotic Analyzer of Tubes
# Copyright (C) 2021 Jaidon Lybbert

# Credit to:
# Pete Shinners - https://www.pygame.org/docs/tut/PygameIntro.html
# Radames Ajna - https://github.com/radames/opencv_video_to_pygame

"""This file and affiliate code in this directory serves to create a desktop
   GUI for recieving and sending data and control signals to the RAT device"""

import numpy as np
import pygame as pg
import cv2 as cv
import sys
sys.path.insert(1, '../../comms/')
import guisocket as sock 

#------- Constant definitions --------#
# Graphics dimensions
SIZE_SCREEN  = SCR_W, SCR_H = 1280, 720
SIZE_CAM     = CAM_W, CAM_H = 640, 480
SIZE_MOV_BUTTONS = MOV_B_H, MOV_B_W = 20, 20
CONTROLS_V_CENTER = (SCR_H - CAM_H) / 2 + CAM_H
MOV_BUTTON_V = CONTROLS_V_CENTER + (1/2*MOV_B_H)
UP_BUTTON_V = MOV_BUTTON_V - MOV_B_H
DOWN_BUTTON_V = MOV_BUTTON_V + MOV_B_H

# Movement control button indicators
LOC_MOV_L_BUTTON = pg.Rect((50, MOV_BUTTON_V) , SIZE_MOV_BUTTONS)
LOC_MOV_R_BUTTON = pg.Rect((90, MOV_BUTTON_V) , SIZE_MOV_BUTTONS)
LOC_INC_SPD_BUTTON = pg.Rect((70, UP_BUTTON_V), SIZE_MOV_BUTTONS)
LOC_DEC_SPD_BUTTON = pg.Rect((70, DOWN_BUTTON_V), SIZE_MOV_BUTTONS)

# Camera control button indicators
LOC_YAW_R_BUTTON = pg.Rect((250, MOV_BUTTON_V), SIZE_MOV_BUTTONS)
LOC_YAW_L_BUTTON = pg.Rect((290, MOV_BUTTON_V), SIZE_MOV_BUTTONS)
LOC_PITCH_UP_BUTTON = pg.Rect((270, UP_BUTTON_V) , SIZE_MOV_BUTTONS)
LOC_PITCH_DN_BUTTON = pg.Rect((270, DOWN_BUTTON_V) , SIZE_MOV_BUTTONS)

# Colors
RED = (255, 0, 0)
GRAY = (56, 56, 56)

# Control Codes
DIR_BACKWARD = 0x0001
DIR_FORWARD  = 0x0002
SPEED_INC    = 0x0004
SPEED_DEC    = 0x0008
YAW_RIGHT    = 0x0010
YAW_LEFT     = 0x0020
PITCH_UP     = 0x0040
PITCH_DOWN   = 0x0080
SEQ_SCAN     = 0x0100

#--------- Initialization -------------#
# Initialize connection
socket = sock.connection_init()
# Screen initialization 
pg.init()
pg.display.set_caption("RAT Human Machine Interface")
screen_size = width, height = 1280, 720 
screen = pg.display.set_mode(screen_size)
pg.Surface.fill(screen, (56, 56, 56))

# Camera window creation
video_size = cam_width, cam_height = 640, 480
camera_window = pg.Surface(video_size)
camera = cv.VideoCapture(0)

# 3D scan results viewer
scan = pg.image.load('scan_result.jpeg')

# Control button indicators
# Movement
move_left_button = pg.Surface(SIZE_MOV_BUTTONS)
move_right_button = pg.Surface(SIZE_MOV_BUTTONS)
spd_inc_button = pg.Surface(SIZE_MOV_BUTTONS)
spd_dec_button = pg.Surface(SIZE_MOV_BUTTONS)
pg.Surface.fill(move_left_button, (255,0,0))
pg.Surface.fill(move_right_button, (255,0,0))
pg.Surface.fill(spd_inc_button, (255,0,0))
pg.Surface.fill(spd_dec_button, (255,0,0))
# Camera
pitch_up_button = pg.Surface(SIZE_MOV_BUTTONS)
pitch_dn_button = pg.Surface(SIZE_MOV_BUTTONS)
yaw_r_button = pg.Surface(SIZE_MOV_BUTTONS)
yaw_l_button = pg.Surface(SIZE_MOV_BUTTONS)
pg.Surface.fill(pitch_dn_button, (255,0,0))
pg.Surface.fill(pitch_up_button, (255,0,0))
pg.Surface.fill(yaw_r_button, (255,0,0))
pg.Surface.fill(yaw_l_button, (255,0,0))
# Text Display
font = pg.font.SysFont('ubuntumono', 32)
lidarOutput = font.render('Lidar distance: 1.2 cm', True, RED, GRAY)
lidarRect = lidarOutput.get_rect()
lidarRect.center = (200, MOV_BUTTON_V - 90)
# Command signal to be sent
command = 0x0000
#--------------------------------------#


def updateCommand(last_command):
    global command
    if last_command == DIR_BACKWARD:
        command = DIR_BACKWARD | (command & ~DIR_FORWARD)
        pg.Surface.fill(move_left_button, (0, 255, 0))
        pg.Surface.fill(move_right_button, (255, 0, 0))
    elif last_command == DIR_FORWARD:
        command = DIR_FORWARD | (command & ~DIR_BACKWARD)
        pg.Surface.fill(move_right_button, (0,255,0))
        pg.Surface.fill(move_left_button, (255,0,0))
    elif last_command == SPEED_INC:
        command = SPEED_INC | (command & ~SPEED_DEC)
        pg.Surface.fill(spd_inc_button, (0, 255, 0))
        pg.Surface.fill(spd_dec_button, (255, 0, 0))
    elif last_command == SPEED_DEC:
        command = SPEED_DEC | (command & ~SPEED_INC)
        pg.Surface.fill(spd_dec_button, (0, 255, 0))
        pg.Surface.fill(spd_inc_button, (255, 0, 0))
    elif last_command == YAW_RIGHT:
        command = YAW_RIGHT | (command & ~YAW_LEFT)
    elif last_command == YAW_LEFT:
        command = YAW_LEFT | (command & ~YAW_RIGHT)
    elif last_command == PITCH_UP:
        command = PITCH_UP | (command & ~PITCH_DOWN)
        pg.Surface.fill(pitch_dn_button, (255, 0, 0))
        pg.Surface.fill(pitch_up_button, (0, 255, 0))
    elif last_command == PITCH_DOWN:
        command = PITCH_DOWN | (command & ~PITCH_UP)
        pg.Surface.fill(pitch_dn_button, (0, 255, 0))
        pg.Surface.fill(pitch_up_button, (255, 0, 0))
    elif last_command == SEQ_SCAN:
        command = SEQ_SCAN


def newLidarScan():
    global scan
    scan = pg.image.load('scan_result.jpeg')


def sendCommand(socket):
    global command
    command_bytes = command.to_bytes(2, 'big')
    socket.sendall(command_bytes)
    sensor_data = socket.recv(4)
    sys_status = socket.recv(4)
    print(sensor_data)
    print(sys_status)


def main():
    global socket
    # Read a frame from the camera w/ openCV (read as numpy array)
    ret, frame = camera.read()
    # Convert default format to format read understood by pygame
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    # Debugging image format
    # print("Width: ", camera.get(3))
    # print("Height: ",  camera.get(4))
    # print(frame.shape)
    # print("Screen wxh: ", screen.get_size())
    # The height and width are swapped in OpenCV vs Pygame
    frame = frame.swapaxes(0, 1)
    
    # Draw camera feed onto the camera_window surface
    pg.surfarray.blit_array(camera_window, frame)
    # Draw camera_window onto screen surface
    screen.blit(camera_window, (0, 0))
    # Update display
    pg.display.update()

    # Draw 3D scan results
    screen.blit(scan, (cam_width, 0))

    # Draw controls button indicators
    screen.blit(move_left_button, LOC_MOV_L_BUTTON)
    screen.blit(move_right_button, LOC_MOV_R_BUTTON)
    screen.blit(spd_dec_button, LOC_DEC_SPD_BUTTON)
    screen.blit(spd_inc_button, LOC_INC_SPD_BUTTON)
    screen.blit(yaw_l_button, LOC_YAW_L_BUTTON)
    screen.blit(yaw_r_button, LOC_YAW_R_BUTTON)
    screen.blit(pitch_dn_button, LOC_PITCH_DN_BUTTON)
    screen.blit(pitch_up_button, LOC_PITCH_UP_BUTTON)

    screen.blit(lidarOutput, lidarRect)
    
    for event in pg.event.get():
        if event.type == pg.QUIT: 
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d:
                updateCommand(DIR_FORWARD)
                print("Moving forward", command)
            elif event.key == pg.K_a:
                updateCommand(DIR_BACKWARD)
                print("Moving backward", command)
            elif event.key == pg.K_s:
                updateCommand(SPEED_DEC)
                print("Decreasing speed", command)
            elif event.key == pg.K_w:
                updateCommand(SPEED_INC)
                print("Increasing speed", command) 
            #elif event.key == pg.K_c:
            #    socket = sock.connection_init()
            elif event.key == pg.K_f:
                sendCommand(socket)


if __name__ == '__main__':
    while 1:
        main()
