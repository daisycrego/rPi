#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import time
from time import sleep

# init LED pwm
LED = 17 

	
# set pin numbering to broadcom scheme
gpio.setmode(gpio.BCM)

gpio.setup(LED, gpio.OUT)

pwm_LED = gpio.PWM(LED, 100)
pwm_LED.start(0)

# freely chosen SPI pins
SPICLK = 16  # BOARD 36
SPIMISO = 19  # BOARD 35
SPIMOSI = 20  # BOARD 38
SPICS = 25  # BOARD 22
 
# set up the SPI interface pins
gpio.setup([SPIMOSI, SPICLK, SPICS], gpio.OUT)
gpio.setup(SPIMISO, gpio.IN)


# 10k trim pot connected to adc #0
potentiometer_adc = 0;


# Execute when a connection has been established to the MQTT server
def connectionStatus(client, userdata, flags, rc):

	mqttClient.subscribe("rpi/gpio")

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        gpio.output(cspin, True)
 
        gpio.output(clockpin, False)  # start clock low
        gpio.output(cspin, False)     # bring CS low
 
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        gpio.output(mosipin, True)
                else:
                        gpio.output(mosipin, False)
                commandout <<= 1
                gpio.output(clockpin, True)
                gpio.output(clockpin, False)
 
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                gpio.output(clockpin, True)
                gpio.output(clockpin, False)
                adcout <<= 1
                if (gpio.input(misopin)):
                        adcout |= 0x1
 
        gpio.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

def read_potentiometer():
    trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    return round(trim_pot / 1024.0, 2)

# Execute when a message has been received from the MQTT server
def messageDecoder(client, userdata, msg):
	# Decode message from topic
	message = msg.payload.decode(encoding='UTF-8')
	
	if message == "poll":
		current_adc = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
		trimmed_val = int(current_adc/10.2)
		if trimmed_val < 0: 
			trimmed_val *= -1
		if trimmed_val > 100: 
			trimmed_val %= 100
		mqttClient.publish("rpi/ios", trimmed_val)
		pwm_LED.ChangeDutyCycle(trimmed_val)

#gpioSetup()

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
