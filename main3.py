#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import RPi.GPIO as gpio

def gpioSetup():
	
	# set pin numbering to broadcom scheme
	gpio.setmode(gpio.BCM)
	# set GPIO21 (pin 40) as output pin
	gpio.setup(21, gpio.OUT)


# Execute when a connection has been established to the MQTT server
def connectionStatus(client, userdata, flags, rc):

	mqttClient.subscribe("rpi/gpio")


# Execute when a message has been received from the MQTT server
def messageDecoder(client, userdata, msg):
	# Decode message from topic
	message = msg.payload.decode(encoding='UTF-8')
	
	# Set GPIO pin to HIGH or LOW
	if message == "on":
		gpio.output(21, gpio.HIGH)
		print("LED is ON!")
	elif message == "off":
		gpio.output(21, gpio.LOW)
		print("LED is OFF!")
	else:
		print("Unknown message: {}".format(message))

# Set up RPI GPIO pins
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



