import os
import sys
import time

import turtle

import tty
import sys
import termios
import uuid
import socketio
import playsound

from threading import Thread


from gtts import gTTS


import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


s1 = 29
s2 = 31
s3 = 33
s4 = 35
s5 = 37

EnaA = 15
In1A = 7
In2A = 5
In1B = 13
In2B = 11
EnaB = 3

GPIO.setmode(GPIO.BOARD)

GPIO.setup(s1, GPIO.IN)
GPIO.setup(s2, GPIO.IN)
GPIO.setup(s3, GPIO.IN)
GPIO.setup(s4, GPIO.IN)
GPIO.setup(s5, GPIO.IN)

GPIO.setup(EnaA, GPIO.OUT)
GPIO.setup(In1A, GPIO.OUT)
GPIO.setup(In2A, GPIO.OUT)
GPIO.setup(EnaB, GPIO.OUT)
GPIO.setup(In1B, GPIO.OUT)
GPIO.setup(In2B, GPIO.OUT)

pwmA = GPIO.PWM(EnaA, 100)
pwmB = GPIO.PWM(EnaB, 100)
pwmA.start(0)
pwmB.start(0)


# def switch_callback(channel):
#     print('Switch pressed, exiting.')
#     GPIO.cleanup()
#     sys.exit(0)


# GPIO.add_event_detect(switch, GPIO.FALLING, callback=switch_callback)


def mottor_conntrol(leftSpeed, rightSpeed):

    # speed *= 100
    # turn *=70

    # speed = 200
    # turn =0
    # leftSpeed = speed-turn
    # rightSpeed = speed+turn
    print(leftSpeed, ":", rightSpeed)
    if leftSpeed > 100:
        leftSpeed = 100
    elif leftSpeed < -100:
        leftSpeed = -100
    if rightSpeed > 100:
        rightSpeed = 100
    elif rightSpeed < -100:
        rightSpeed = -100

    pwmA.ChangeDutyCycle(abs(leftSpeed))
    pwmB.ChangeDutyCycle(abs(rightSpeed))
    if leftSpeed > 0:
        GPIO.output(In1A, GPIO.HIGH)
        GPIO.output(In2A, GPIO.LOW)
    else:
        GPIO.output(In1A, GPIO.LOW)
        GPIO.output(In2A, GPIO.HIGH)
    if rightSpeed > 0:
        GPIO.output(In1B, GPIO.HIGH)
        GPIO.output(In2B, GPIO.LOW)
    else:
        GPIO.output(In1B, GPIO.LOW)
        GPIO.output(In2B, GPIO.HIGH)


def stop():
    print("Stop")
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)


def read_line():
    line = [GPIO.input(s1), GPIO.input(s2), GPIO.input(s3),
            GPIO.input(s4), GPIO.input(s5)]

    if line == [1, 1, 1, 1, 0]:
        line_error = 4
    elif line == [1, 1, 1, 0, 0]:
        line_error = 3
    elif line == [1, 1, 1, 0, 1]:
        line_error = 2
    elif line == [1, 1, 0, 0, 1]:
        line_error = 1
    elif line == [1, 1, 0, 1, 1]:
        line_error = 0
    elif line == [1, 0, 0, 1, 1]:
        line_error = -1
    elif line == [1, 0, 1, 1, 1]:
        line_error = -2
    elif line == [0, 0, 1, 1, 1]:
        line_error = -3
    elif line == [0, 1, 1, 1, 1]:
        line_error = -4
    else:
        line_error = 0
    return line_error



P = 65
I = 15
D = 5

baseSpeed = 19
line_error = 0
oldErrorP = 0
errorI = 0


def pid_start():
    global oldErrorP
    global line_error
    global baseSpeed
    global errorI

    errorP = line_error
    errorD = errorP - oldErrorP
    errorI = (2.5 / 3.0) * errorI + errorP

    totalError = P * errorP + D * errorD + I * errorI
    oldErrorP = errorP

    RMS = baseSpeed + totalError
    LMS = baseSpeed - totalError

    return LMS, RMS


filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)


mode_list = ["1", "2", "3"]
room_list = ["4", "5", "6", "7", "8", "9", "0"]
mode = 0
key = 0
key_now = None


def getkey():
    while True:
        try:
            global key
            key = sys.stdin.read(1)[0]
            # if key == "esc":
            #     GPIO.cleanup()
            #     # t1.stop()
            #     # t2.stop()
            #     sys.exit(0)
        except KeyboardInterrupt:
            print('Switch pressed, exiting.')
            GPIO.cleanup()
            # t1.stop()
            # t2.stop()
            sys.exit(0)


def auto_mode():
    global key
    global line_error

    error_now = read_line()
    line_error = (line_error + error_now)/21
    LMS, RMS = pid_start()

    # print(f"{LMS} , {RMS} ")
    mottor_conntrol(LMS, RMS)


def manual_mode():
    if key_now == "A":
        # print("Tien")
        mottor_conntrol(40, 40)
    elif key_now == "B":
        # print("Lui")
        mottor_conntrol(-40, -40)
    elif key_now == "C":
        # print("Phai")
        mottor_conntrol(-50, 50)
    elif key_now == "D":

        mottor_conntrol(50, -50)
        # print("Trai")
    else:
        stop()
        # print(f"Key: {key_now}")


def car_controll():
    global key
    global key_now
    global mode

    while True:
        try:
            if key != None:
                key_now = key
                key = None
            else:
                key_now = None

            if key_now != None:
                # print(key_now)
                if key_now in mode_list:
                    mode = int(key_now)
                if key_now in room_list:
                    print("asvcasvhchvsagcvhas")
                    sio.emit('lengocson/room', key_now)

            if mode == 1:
                pass
            elif mode == 2:
                manual_mode()
            elif mode == 3:
                auto_mode()

            time.sleep(0.05)
        except KeyboardInterrupt:
            print('Switch pressed, exiting.')
            GPIO.cleanup()
            sys.exit(0)


sio = socketio.Client()
sio.connect('http://103.161.112.166:9980')


@sio.event
def connect():
    print("I'm connected!")


@sio.event
def message(data):
    print('I received a message!')


@sio.on('lengocson/mode')
def on_message(data):
    print(f'I received a message!{data}')


@sio.on('lengocson/speed')
def on_message(data):
    fileName = f'{uuid.uuid4()}.mp3'
    tts = gTTS(text=data, lang='vi', slow=False)
    tts.save(fileName)
    playsound.playsound(fileName)
    os.remove(fileName)

# @sio.on('lengocson/mp3')
# def on_message(data):
#     playsound.playsound("sound.mp3", False)
#     print(f'I received a message!{data}')


reader = SimpleMFRC522()


def get_rfid():
    while True:
        id, text = reader.read()
        sio.emit('lengocson/room', id)
        print(id)
        print(text)
        time.sleep(1)


t1 = Thread(target=getkey)
t2 = Thread(target=car_controll)
t3 = Thread(target=get_rfid)
t1.start()
t2.start()
t3.start()
