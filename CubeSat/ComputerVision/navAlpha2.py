from os import sys, path
import time
import math
import argparse

# Adding socket stuff---------------------

import socket

sock = socket.socket()
# ip = '127.0.0.1'
ip = '192.168.43.209' #SimPlat ip
# ip = '192.168.1.23' #simplat ip at jonathan ung's house
port = 12345
#sock.connect((ip, port))

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# from opencv.lib_aruco_pose import *
from arucotracklib import *

# --------------------------------------------------
# -------------- FUNCTIONS
# --------------------------------------------------

# Goal of this navigation is to have CubeSat Rotate a degree/ angle; with the goal of
# having the target aligned in its center before thrusting toward target.

# ---HEADING CONTROLS
# By knowing how long SimPlat takes to rotate a full 360 we can computer the amount of
# time it takes to move N degrees.
# Now that we have time it takes to rotate a certain degree/angle, we can use this to send a
# rotate command for X amount of seconds before sending counter thrusting to stop rotation .
# This will line us up with the target in the center of our screen.

# XYZ -> Angle-> Rotate(angle) ->computeRotateTime(angel) ->startRotate(seconds )

thrustDic = {'Stop': '00000000',
             'Left': '01100000',
             'Right': '00000110',
             'Forward': '00011000',
             'Backward': '10000001',
             'UpperRightDiagonal': '00011110',
             'UpperLeftDiagonal': '01111000',
             'BottomRightDiagonal': '10000111',
             'CounterClockWise': '01010101',
             'ClockWise': '10101010'}

reverseDic = {'Stop': 'Stop',
              'Left': 'Right',
              'Right': 'Left',
              'Forward': 'Backward',
              'Backward': 'Forward',
              'CounterClockWise': 'ClockWise',
              'ClockWise': 'CounterClockWise'}

distanceGoal = 30.0

def marker_position_to_angle(x, y, z):
    angle_x = math.degrees(math.atan2(x, z))
    angle_y = math.degrees(math.atan2(y, z))

    return (angle_x, angle_y)


def initialSearch():
    while True:
        marker_found, x, y, z = aruco_tracker.track(loop=False)
        if marker_found is True:
           sock.send(sendCommand('Stop').encode())
           break
    return

def checkCenterTreshhold(currentX):
    # function takes in the current x value from the camera and checks to see if the target is near the the center threshhold of the camera
    # if the target is outside the thresh hold, return false. if the target is within center thresh hold, return true
    # change min and max value as neccessary to change threshold
    minX = -20.0
    maxX = 20.0
    if currentX < minX or currentX > maxX:
        return False
    return True


def checkDistanceThreshhold(currentZ):
    # function takes in current z value from camera and checks to see if the distance between cubesat and the target is within the goal
    # if the distance is too great, return false. if the distance is within the goal, return true
    if currentZ > distanceGoal:
        return False
    return True


def headerControl(degree):
    # if the degree is negative, that means the target is to the left of CubeSat so a clockwise rotation is neccessary,
    # else if the degree is positive, the target is to the right of CubeSat so a counter-clockwise rotation is needed
    if degree < 0:
        thrustCommand = 'ClockWise'
    elif degree > 0:
        thrustCommand = 'CounterClockWise'
    else:
        # print("Stop")'
        thrustCommand = 'Stop'

    return thrustCommand


def headerHelper(command):
    #recursion function to loop until the threshold is satisfied
    while True:
        marker_found, x, y, z = aruco_tracker.track(loop=False)
        checker = checkCenterTreshhold(x)
        if checker is True:
#            sock.send(sendCommand(reverseCommand(command)).encode())
            break
    return

def velocityControl(dist):
    if dist > distanceGoal:
        delayCommand = 'Forward'
    if dist <= distanceGoal:
        delayCommand = 'Stop'

    return delayCommand

def velocityHelper():
    #recursion function that keeps forward command going until either target is off center or cubesat is within distance
    while True:
        marker_found, x, y, z = aruco_tracker.track(loop=False)
        checker = checkDistanceThreshhold(z)
        if checker is True:
           break
    return

def sendCommand(command):

    print(f'Command: {command}')
    return thrustDic[command]

def reverseCommand(command):

    return reverseDic[command]


# --------------------------------------------------
# -------------- CONNECTION
# --------------------------------------------------
# -- Connect to the vehicle
print('Connecting...')

# --------------------------------------------------
# -------------- LANDING MARKER
# --------------------------------------------------
# --- Define Tag
id_to_find = 24
marker_size = 10  # - [cm]

# --- Get the camera calibration path
# Find full directory path of this script, used for loading config and other files
cwd = path.dirname(path.abspath(__file__))
calib_path = cwd + "/../opencv/"
camera_matrix = np.loadtxt('cameraMatrix_raspi.txt', delimiter=',')
camera_distortion = np.loadtxt('cameraDistortion_raspi.txt', delimiter=',')
aruco_tracker = ArucoSingleTracker(id_to_find=id_to_find, marker_size=marker_size, show_video=False,
                                   camera_matrix=camera_matrix, camera_distortion=camera_distortion)

time_0 = time.time()

while True:

    # (x,y, z) add test values
    marker_found, x, y, z = aruco_tracker.track(loop=False)  # Note : XYZ  are all in cm
    x = -x

    print(f'taget found? {marker_found}')
    if marker_found:
        angle_x, angle_y = marker_position_to_angle(x, y, z)

        # print(f'X:{x} Y:{y}, Z:{z}, angleX:{angle_x}')
        angle_x, angle_y = marker_position_to_angle(x, y, z)
        withinCenter = checkCenterTreshhold(x)
        withinDistance = checkDistanceThreshhold(z)

        if withinCenter is False and withinDistance is False:
            # if both checks fail meaning the distance is larger than the goal and the target is not within center threshold
            print('outside of center threshold and distance threshold')
            delayed = headerControl(angle_x)
            #sends rotation command first, enters loop until target is recentered, then sends counterthrust            sock.send(sendCommand(delayed).encode())
#            response = sock.recv(1024).decode()
#            if response != sendCommand(delayed):
#                sock.send(sendCommand(delayed).encode())
            headerHelper(delayed)
#            sock.send(sendCommand(reverseCommand(delayed)).encode())
            time.sleep(0.5)
        elif withinCenter is True and withinDistance is False:
            # the target is within center threshold but is outside distance goal
            print('target within center threshold but outside distance goal')
            delayed = velocityControl(z)
            #sends forward thrust, loops until either target is off center or target is within distance, then sends backward thrust
#            sock.send(sendCommand(delayed).encode())
#            response = sock.recv(1024).decode()
#            if response != sendCommand(delayed):
#                sock.send(sendCommand(delayed).encode())
            velocityHelper()
#            time.sleep(4)
#            sock.send(sendCommand(reverseCommand(delayed)).encode())
            time.sleep(0.5)
        elif withinCenter is False and withinDistance is True:
            # target is within distance goal but not within center threshold
            print('target within distance goal but outside center threshold')
            delayed = headerControl(angle_x)
            # sends rotation command first, enters loop until target is recentered, then sends counterthrust
            sock.send(sendCommand(delayed).encode())
#            response = sock.recv(1024).decode()
#            if response != sendCommand(delayed):
#                sock.send(sendCommand(delayed).encode())
            headerHelper(delayed)
#            sock.send(sendCommand(reverseCommand(delayed)).encode())
            time.sleep(0.5)
        elif withinDistance is True and withinCenter is True:
            # to do: figure out what to do when everything is perfect
            print('do nothing')
            

        # --- COmmand to land
        if z <= distanceGoal:
            print(" -->>Target Distination Reached <<")

    if marker_found is False:
#        sock.send(sendCommand('ClockWise').encode())
        print('Searching for target...')
        initialSearch()
#        sock.send(sendCommand('Stop').encode())
        time.sleep(0.5)
