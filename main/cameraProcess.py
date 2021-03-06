# Technically combination of captureImage and imageProcessing
# Also interface for connect with PC2's Arduino that communicate /w PC1's Arduino
# a complete flow of capture / image processing / send to serial command.
# -by borBier(11/18/2018)

# Library and dependencies.
import subprocess
import os
import signal

import time
import serial

import numpy as numpy
import matplotlib.pyplot as plt
import cv2

# Configuration.
sendingTime = 2.0

captureTime = 30.0
imageDirectory = "C:/out/"          # Please use "/" format
imageDirectory = "D:/Project/datacomm-assignment/image-processing/"
imageFile = "img-1.bmp"
threshold = 127

target = imageDirectory + imageFile

# ===== List serial ports. =====
def listSerialPorts():
    result = []
    ports = []
    for i in range(256):
        ports.append('COM%s' % (i + 1))
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

# ===== Take an image from camera and process it =====
def capture():
    print("! Capturing the image . . . ")
    os.chdir("C:\Program Files (x86)\Java\jdk1.8.0_74\\bin")
    capture = subprocess.Popen(["java","code.SimpleRead"]).pid
    time.sleep(captureTime)
    os.kill(capture, signal.SIGTERM)

def quadrantProcess(img):
    unique, counts = numpy.unique(img, return_counts=True)
    occurance = dict(zip(unique, counts))
    try:
        return ("0" if occurance[0] > occurance[255] else "1")
    except KeyError:
        keys = list(occurance.keys())
        return ("0" if keys[0] == 0 else "1")

def imageCrop(img):
    (h, w) = img.shape[:2]

    upperLeft = img[0:int(h/2) , 0:int(w/2)]
    upperRight = img[0:int(h/2), int(w/2):w]
    lowerLeft = img[int(h/2):h, 0:int(w/2)]
    lowerRight = img[int(h/2):h, int(w/2):w]

    return [upperRight, upperLeft, lowerLeft, lowerRight]

#
#  Format : XXXX1XXXX2XXXX3XXXX4
#  20 output >> 5 out/quadrant >> 4 out for sub-quadrant + 1 for overall
def imgProcess():
    img = cv2.imread(target, 0)
    ret, binaryImg = cv2.threshold(img, threshold, 256, cv2.THRESH_BINARY)
    splited = imageCrop(binaryImg)
    result = ""
    for i in range(4):
        part = splited[i]
        quadrant = imageCrop(part)
        for i in range(4):
            result = result + quadrantProcess(quadrant[i])
        result = result + quadrantProcess(part)
    return result

# ===== Send result to serial ======       
def sendSerial(message):
    for i in range(len(message)):
        print(message[i])
        ser.write(message[i].encode('utf-8'))
        time.sleep(sendingTime)



# ===== Main =====

# List available ports.
availablePort = listSerialPorts()
print("===== Available Serial Ports =====")
for i, s in enumerate(availablePort):
    print(str(i) + ' ' + s)

# Connect to serial port.
selectedPort = int(input("Select COM port by index >> "))
ser = serial
try:
    ser = serial.Serial(port=availablePort[selectedPort], baudrate=9600,timeout=10)
    print('connected!')
    print(ser.inWaiting())
except serial.serialutil.SerialException:
    print('Exception occured during connecting to COM',selectedPort)

# Capture image and image processing.
capture()
imgResult = imgProcess()
print("Result : ", imgResult)

sendSerial(imgResult)