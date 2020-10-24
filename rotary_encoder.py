from RPi import GPIO
from time import sleep

clk1 = 17
dt1 = 18
clk2 = 22 
dt2 = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(clk2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

counter1 = 0
counter2 = 0
clk1LastState = GPIO.input(clk1)
clk2LastState = GPIO.input(clk2)

try:
        while True:
                clkState1 = GPIO.input(clk1)
		clkState2 = GPIO.input(clk2)
                dtState1 = GPIO.input(dt1)
		dtState2 = GPIO.input(dt2)
                if clkState1 != clk1LastState:
                        if dtState1 != clkState1:
                                counter1 += 1
                        else:
                                counter1 -= 1
                        print('1: {}'.format(counter1))
                if clkState2 != clk2LastState:
			if dtState2 != clkState2: 
				counter2 += 1
			else:
				counter2 -= 1
			print('2: {}'.format(counter2))
		clk1LastState = clkState1
		clk2LastState = clkState2
                sleep(0.01)
finally:
        GPIO.cleanup()

