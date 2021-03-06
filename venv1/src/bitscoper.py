#!/usr/bin/env python

import paho.mqtt.client as mqtt
from time import sleep
import RPi.GPIO as gpio
import threading
import json
import numpy as np
from bitscope import *

MY_RATE = 1000 # default sample rate in Hz we'll use for capture.
#MY_SIZE = 12288 # number of samples we'll capture - 12288 is the maximum size
MY_SIZE = 10
clientName = "RPI"
serverAddress = "192.168.1.6"
mqttClient = None

# Instantiate eclipse pago as mqttclient
mqttClient = mqtt.Client(clientName)

# Execute when a connection has been established to the MQTT server
def connectionStatus(client, userdata, flags, rc):
    mqttClient.subscribe("rpi/gpio")

def messageDecoder(client, userdata, msg):
    # Decode message from topic
    message = msg.payload.decode(encoding='UTF-8')
    print("Unknown message: {}".format(message))

# set calling functions on mqttclient
mqttClient.on_connect = connectionStatus
mqttClient.on_message = messageDecoder

# connect client to server
mqttClient.connect(serverAddress)

def foreground():
    # monitor client activity forever
    mqttClient.loop_forever()

def background():
    clk1 = 17
    dt1 = 18
    clk2 = 22
    dt2 = 23
    counter1 = 0
    counter2 = 0
    clkState1 = 0
    clkState2 = 0

    # set pin numbering to broadcom scheme
    gpio.setmode(gpio.BCM)

    gpio.setup(clk1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(clk2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(dt1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(dt2, gpio.IN, pull_up_down=gpio.PUD_DOWN)

    clk1LastState = gpio.input(clk1)
    clk2LastState = gpio.input(clk2)

    while True:
        clkState1 = gpio.input(clk1)
        clkState2 = gpio.input(clk2)
        dtState1 = gpio.input(dt1)
        dtState2 = gpio.input(dt2)
        if clkState1 != clk1LastState:
            if dtState1 != clkState1:
                counter1 += 1
            else:
                counter1 -= 1
        if clkState2 != clk2LastState:
            if dtState2 != clkState2:
                counter2 += 1
            else:
                counter2 -= 1
        clk1LastState = clkState1
        clk2LastState = clkState2

        dials = {
                "dial1": counter1,
                "dial2": counter2
        }

        jsonDials = json.dumps(dials)
        print(jsonDials)

        mqttClient.publish("rpi/ios", jsonDials)
        sleep(.01)

def bitscope_thread():
    #open bitscope micro
    scope = Scope("",1)
    # print some details about the device
    print("Name = {}, Version = {}, ID = {}, Count = {}".format(scope.devices[0].name,scope.devices[0].version,scope.devices[0].id,scope.device_count))

    scope.devices[0].mode(MODE.FAST)

    for channel in scope.devices[0].channels:
        channel.configure(
            source=SOURCE.BNC,
            offset=ZERO,
            range=scope.device_count,
            coupling=COUPLING.RF
        )
    channel.enable()

    # trace for a particular device once
    scope.tracer.trace(0.01,TRACE.SYNCHRONOUS)
    while True:
        #Vector storing time-data for x-axis
        x = np.arange(MY_SIZE)/float(MY_RATE)

        # acquire data from the required device and channel
        channelAdata = scope.devices[0].channels[0].acquire()
	channelBdata = scope.devices[0].channels[1].acquire()
        channels = {
            "a": channelAdata,
            "b": channelBdata
	}
	payload = json.dumps(channels)
        print(json.dumps(channels, indent=4, sort_keys=True))
        mqttClient.publish("rpi/scope", payload)
        sleep(.01)

f = threading.Thread(name="foreground", target=foreground)
b = threading.Thread(name="background", target=background)
scope = threading.Thread(name="scope", target=bitscope_thread)

f.start()
#b.start()
scope.start()
