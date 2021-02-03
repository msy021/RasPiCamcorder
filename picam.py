#!/usr/bin/env python2.7
# script by Alex Eames http://RasPi.tv
# needs RPi.GPIO 0.5.2 or later
# No guarantees. No responsibility accepted. It works for me.
# If you need help with it, sorry I haven't got time. I'll try and add more
# documentation as time goes by. But no promises.

#https://www.techoism.com/install-mp4box-gpac/



#"Based on RasPiCamcorder scripts by Alex Eames of http://RasPi.TV/
#https://github.com/raspitv/RasPiCamcorder/https://github.com/raspitv/RasPiCamcorder/"

import RPi.GPIO as GPIO
from subprocess import call
import subprocess
from time import sleep
import time
import sys
import os
import datetime as dt

base_vidfile = "raspivid -t 1200000 -o "
#filename = dt.datetime.now().strftime('/home/pi/vid%d-%m-%Y-%H:%M:%S.h264')
filename = dt.datetime.now().strftime('/home/pi/%Y-%m-%d-%H,%M,%S')
recording = 0
time_off = time.time()
last_time = time.time() 

GPIO.setmode(GPIO.BCM)
#GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN)
GPIO.setup(2, GPIO.OUT)
GPIO.output(2, 1)

def shutdown():
    print "shutting down now"
    #stop_recording()
    #flash(0.05,50)
    GPIO.cleanup()
    os.system("sudo halt")
    sys.exit()

def flash(interval,reps):
    for i in range(reps):
        GPIO.output(2, 0)
        sleep(interval)
        GPIO.output(2, 1)
        sleep(interval)

def start_recording():
    global recording
    global filename
    if recording == 0:
        filename = dt.datetime.now().strftime('/home/pi/%Y-%m-%d-%H,%M,%S')
        vidfile = base_vidfile + filename # + str(rec_num).zfill(5)
        vidfile += ".h264 -fps 24 -b 25000000 -w 1600 -h 1200 -vs" #-w 1280 -h 720 -awb tungsten
        print "starting recording\n%s" % vidfile
        time_now = time.time()
        #if (time_now - time_off) >= 0.3:
        #    if front_led_status != 0:
        #       GPIO.output(5, 1)
        #   GPIO.output(22, 1)
        recording = 1
        call ([vidfile], shell=True)
        recording = 0 # only kicks in if the video runs the full period
    else : print "already recording"

def stop_recording():
    global recording
    global time_off
    time_off = time.time()
    print "stopping recording"
    #GPIO.output(5, 0)
    #GPIO.output(22, 0)
    call (["pkill raspivid"], shell=True)
    command = "MP4Box -fps 24 -add " + filename + ".h264 " + filename + ".mp4"
    call([command], shell=True)
    print("\r\nRasp_Pi => Video Converted! \r\n")
    recording = 0

# threaded callback function runs in another thread when event is detected
# this increments variable rec_num for filename and starts recording
def my_callback2(channel):
    print ("interrupt")
    global rec_num
    global last_time
    time_now = time.time()
    if (time_now - time_off) >= 0.3 and (time_now - last_time) >= 0.3 :
        print ("record button pressed")
        #rec_num += 1
        if recording == 0:
            #write_rec_num()
            flash(0.1,4) # interval,reps
            start_recording()
            
        else:
            flash(0.02,20) # interval,reps
            print ("already recording....")
    else:
        print ("interval prea scurt")
    last_time = time.time()
        


GPIO.add_event_detect(3, GPIO.FALLING, callback=my_callback2)

try:

    while True:
        # this will run until button attached to 24 is pressed, then 
        # if pressed long, shut program, if pressed very long shutdown Pi
        # stop recording and shutdown gracefully
        print "Waiting for button press" # rising edge on port 24"
        #GPIO.wait_for_edge(3, GPIO.FALLING)
        time_now = time.time()
        while GPIO.input(3):
            sleep(0.05)
            if not recording:
                if (time.time()-time_now) >= 0.3 :
                    GPIO.output(2, 0)
                if (time.time()-time_now) >= 0.6:
                    GPIO.output(2, 1)
                    time_now = time.time()
            else :
                GPIO.output(2, 0)
            #GPIO.output(2, not recording)
        print "button pressed"
        #stop_recording()

        # poll GPIO 24 button at 20 Hz continuously for 3 seconds
        # if at the end of that time button is still pressed, shut down
        # if it's released at all, break
        for i in range(60):
            sleep(0.05)
            if GPIO.input(3):
                break
            if 0 <= i < 25: 
                GPIO.output(2, 0)
            if 25 <= i < 58: 
                GPIO.output(2, 1)
            if i >= 59:
                GPIO.output(2, 0)
        
        if 25 <= i < 58:              # if released between 1.25 & 3s close prog
            print "stop recording"
            flash(0.2,3) # interval,reps
            stop_recording()
            #GPIO.cleanup()
            #sys.exit()

        if 0 <= i < 25:              # if released between 1.25 & 3s close prog
            if not recording :
                print "start recording"
            if recording : 
                print ("already recording")
                flash(0.02,5) # interval,reps
            #flash(0.1,6) # interval,reps
            #start_recording()
            #GPIO.cleanup()
            #sys.exit()
            

        if not GPIO.input(3):
            if i >= 59:
                flash(0.02,50) # interval,reps
                shutdown()
                print "shutdown"

except KeyboardInterrupt:
    print "ctrl c pressed"
    #stop_recording()
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
