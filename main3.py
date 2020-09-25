#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import time

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
	
	if message == "toggleLED":
		print("toggleLED, swapping LED state")
		if gpio.input(21):
			gpio.output(21,gpio.LOW)
			mqttClient.publish("rpi/gpio", "switchOn")
		else:
			gpio.output(21,gpio.HIGH)
			mqttClient.publish("rpi/gpio", "switchOff")
	if message == "on":
		gpio.output(21, gpio.HIGH)
		print("set pin 21 (LED) to ON")
	elif message == "off":
		gpio.output(21,gpio.LOW)
		print("set pin 21 (LED) to OFF")
	else:
		print("Unknown message: {}".format(message))

def button_callback(channel):
   print("Button pressed")
   mqttClient.publish("rpi/gpio", "buttonPressed")


# Set up RPI GPIO pins
gpioSetup()

clientName = "RPI"
serverAddress = "192.168.1.6"

# Instantiate eclipse pago as mqttclient
mqttClient = mqtt.Client(clientName)

# set calling functions on mqttclient
mqttClient.on_connect = connectionStatus
mqttClient.on_message = messageDecoder

# Set up button
gpio.setup(15, gpio.IN, pull_up_down=gpio.PUD_DOWN) # Set pin 15 to be an input pin and set initial value to be pulled low (off)
gpio.add_event_detect(15,gpio.RISING,callback=button_callback) # Setup event on pin 15 rising edge

# connect client to server
mqttClient.connect(serverAddress)

# monitor client activity forever
mqttClient.loop_forever()



