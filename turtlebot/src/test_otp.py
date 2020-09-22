import Jetson.GPIO as GPIO
import 

def otp_check():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(33, GPIO.IN)
	GPIO.setup(34, GPIO.IN)
	count = 0
	state = 0
	while(1):
		if GPIO.input(33) == 1:
			state = 1
			break
		elif GPIO.input(34) == 1:
			starte = 0
			sleep(1)
			break
	return state




