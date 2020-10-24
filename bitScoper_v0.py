#!/usr/bin/env python

import paho.mqtt.client as mqtt
from time import sleep
import RPi.GPIO as gpio

def gpioSetup():
	# set pin numbering to broadcom scheme
        gpio.setmode(gpio.BCM)

        clk1 = 17
        dt1 = 18
        clk2 = 22
        dt2 = 23

        gpio.setup(clk1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.setup(clk2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.setup(dt1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.setup(dt2, gpio.IN, pull_up_down=gpio.PUD_DOWN)

        counter1 = 0
        counter2 = 0
        clk1LastState = gpio.input(clk1)
        clk2LastState = gpio.input(clk2)

# Execute when a connection has been established to the MQTT server
def connectionStatus(client, userdata, flags, rc):
	mqttClient.subscribe("rpi/gpio")

def messageDecoder(client, userdata, msg):
        # Decode message from topic
        message = msg.payload.decode(encoding='UTF-8')
	if message == "poll":
		enc1, enc2 = read_encoders()
		mqttClient.publish("rpi/ios", (enc1, enc2))
	else:
        	print("Unknown message: {}".format(message))

def read_encoders():
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
	return (counter1, counter2)

gpioSetup()

clientName = "RPI"
serverAddress = "192.168.1.6"

# Instantiate eclipse pago as mqttclient
mqttClient = mqtt.Client(clientName)

# set calling functions on mqttclient
mqttClient.on_connect = connectionStatus
mqttClient.on_message = messageDecoder

# connect client to server
mqttClient.connect(serverAddress)

# monitor client activity forever
mqttClient.loop_forever()

