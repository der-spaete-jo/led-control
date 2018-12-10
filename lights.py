from __future__ import print_function

import RPi.GPIO as GPIO
import time
import math
import random
from multiprocessing.dummy import Pool as ThreadPool 

import xbox


GPIO_PIN_1 = 16
GPIO_PIN_2 = 5
GPIO_PIN_3 = 25
GPIO_PIN_4 = 22
LED_COUNT = 4

GAME_SPEED_RECIPROCALS = [0.75, 1, 1.5, 2]


MAIN_LOOP_DELAY = 0.001
GAME_SHOW_DELAY = 0.6
GAME_INPUT_DELAY = 0.3
STD_DELAY = 0.15


class LedControllerBase():
	def __init__(self, *args):
		self.pins = [a for a in args]
		self.post_init()
		
	def post_init(self):
		# Call GPIO pins via their number.
		GPIO.setmode(GPIO.BCM)

		# Set directions of pins.
		for p in self.pins:
			GPIO.setup(p, GPIO.OUT)
		
	def phase(self, code, delay=0):		
		status = [GPIO.HIGH if self.pins.index(p) in code else GPIO.LOW for p in self.pins]
		map(lambda a: GPIO.output(*a), zip(self.pins, status))
		time.sleep(delay)
		"""for p in self.pins:
			if self.pins.index(p) in code:
				GPIO.output(p, GPIO.HIGH)
			else:
				GPIO.output(p, GPIO.LOW)"""
			
		
	def test(self):
		for i in range(len(self.pins)):
			self.blink([i], 0.3)
		self.stop()
		return time.time
		
			
	def blink(self, code, delay1=0.5, delay2=0, rounds=1):
		for i in range(rounds):
			self.phase(code)
			time.sleep(delay1)
			self.stop()
			time.sleep(delay2 if delay2 else delay1)
		return time.time
		
		
	def disco_mode(self, rounds=100):
		print("DISCO")
		comb = [[0], [1], [2], [3], [0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3], [0, 1, 2], [1, 2, 3], [0, 2, 3], [0, 1, 3]]
		for i in range(rounds):
			s = random.random()				
			self.phase(random.choice(comb))
			time.sleep(0.2*s)
		self.stop()
		return time.time
		
	
	def raupe(self, delay=0.3, rounds=20, rev=False):
		pc = len(self.pins)
		for i in range(rounds):
			for j in range(pc):
				self.phase([j]) if not(rev) else self.phase([pc-j-1])
				time.sleep(delay)
		self.stop()
		return time.time
						
	
	def progress_mode(self, delay=0.3, rounds=1, rev=False, inv=False):
		pc = len(self.pins)
		for i in range(rounds):
			for j in range(pc):
				if inv:
					j = pc-j
				else:					
					j=j+1	
				self.phase(list(range(j))) if not(rev) else self.phase([pc-k-1 for k in range(j)])
				time.sleep(delay)
		self.stop()
		return time.time
		
	def show_off(self):
		print("Showing all modes")
		delay=0.5
		print("LedControllerBase.test()")
		self.test()
		time.sleep(delay)
		print("LedControllerBase.raupe(rounds=2)")
		self.raupe(rounds=2)
		time.sleep(delay)
		print("LedControllerBase.raupe(rounds=2, rev=True)")
		self.raupe(rounds=2, rev=True)
		time.sleep(delay)
		print("LedControllerBase.progress_mode(rounds=2)")
		self.progress_mode(rounds=2)
		time.sleep(delay)
		print("LedControllerBase.progress_mode(rounds=2, rev=True)")
		self.progress_mode(rounds=2, rev=True)
		time.sleep(delay)
		print("LedControllerBase.progress_mode(rounds=2, inv=True)")
		self.progress_mode(rounds=2, inv=True)
		time.sleep(delay)
		print("LedControllerBase.progress_mode(rounds=2, rev=True, inv=True)")
		self.progress_mode(rounds=2, rev=True, inv=True)
		time.sleep(delay)
		print("LedControllerBase.disco_mode(rounds=20)")
		self.disco_mode(rounds=20)
				
	def stop(self):
		""" All pins LOW """
		for p in self.pins:
			GPIO.output(p, GPIO.LOW)
			
						
#How to threading...
#pool = ThreadPool(4) 
#results = pool.map(my_function, my_array)

	


class SimpleGame():
	def __init__(self, led_controller, speed):
		self.LEDC = led_controller
		self.speed_factor = 1/speed
		
	def forge_sequence(self, lngth):
		seq=[]
		for i in range(lngth):
			p = random.choice(self.LEDC.pins)
			seq.append(self.LEDC.pins.index(p))
		#print(seq)
		return seq
		
	def show_sequence(self, seq):
		#map(lambda a: self.LEDC.phase(*a), zip([[self.LEDC.pins[s]] for s in seq], [1 for i in range(len(seq))]))
		for s in seq:
			self.LEDC.blink([s], delay1=self.speed_factor * GAME_SHOW_DELAY, delay2=self.speed_factor * 0.33 * GAME_SHOW_DELAY)
			
	def run(self):
		""" Governs the game process. """
		print("Starting Simple Game")
		self.LEDC.progress_mode()
		self.LEDC.stop()		
		N=3
		while 1:
			# game loop
			# show the current round, forge a new sequence, show it, initialize game variables.
			time.sleep(0.5)
			self.LEDC.blink(list(range(len(self.LEDC.pins))), delay1=self.speed_factor*GAME_SHOW_DELAY, delay2=self.speed_factor * 0.33 * GAME_SHOW_DELAY, rounds=N)
			self.LEDC.stop()

			time.sleep(0.5)
			seq = self.forge_sequence(N)
			print(seq)
			self.show_sequence(seq)
			no = 0
			checked = False
			pick = []

			while 1:
				# guessing round
				# wait for input, if any show it. If gamepad button is released, check the guess.
				if joy.Back():
					self.LEDC.progress_mode(inv=True)
					return N-1
				inpt = [joy.A(), joy.B(), joy.X(), joy.Y()]
				pick = [inpt.index(el) for el in inpt if el] if not pick else pick
				self.LEDC.phase(pick)
				
				if pick and not checked and not any([joy.A(), joy.B(), joy.X(), joy.Y()]):
					self.LEDC.stop()
					print(str(pick[0]), end=', ')
					checked = True
					if len(pick)==1 and seq[no]==pick[0]:
						no=no+1
						checked = False
						pick = []						
					else:
						print("You Lose")
						self.LEDC.disco_mode(rounds=20)
						return N-1
				if no>=N:
					print()
					break
				time.sleep(MAIN_LOOP_DELAY)
										
			N=N+1
		return N
			
	
def polar_coords(x,y):
	radius = math.sqrt(x**2 + y**2)
	angle = 0.0
	if x==0.0 and y==0.0:
		angle = 90.0
	elif x>=0.0 and y>=0.0:
		# first quadrant
		angle = math.degrees(math.atan(y/x)) if x!=0.0 else 90.0
	elif x<0.0 and y>=0.0:
		# second quadrant
		angle = math.degrees(math.atan(y/x))
		angle += 180.0
	elif x<0.0 and y<0.0:
		# third quadrant
		angle = math.degrees(math.atan(y/x))
		angle += 180.0
	elif x>=0.0 and y<0.0:
		# third quadrant
		angle = math.degrees(math.atan(y/x)) if x!=0.0 else -90.0
		angle += 360.0
	return angle, radius
			
			
			
def keyboard_mainloop(LEDC):
	switch_to_joy = 0		
	while 1:
		mode = raw_input("Chose mode...\nj - gamepad (Switch to gamepad control) \nr - raupe \nMode: ")
		if mode == 'x':			
			LEDC.stop()	
			break
		elif mode == 'j':
			switch_to_joy = 1		
			break
		if mode == 'n':
			LEDC.normal_mode()
			LEDC.stop()					
		elif mode == 's':				
			print("Change GPIO pin numbers..")
			a = split(raw_input('Enter up to 4 pin numbers in the format ' + "{0} {1} {2} {3}".format(GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3,GPIO_PIN_4)), ' ')
			LEDC = LedControllerBase(*a) 
			print('To permanently change the pin numbers please open "lights.py" in a text editor of your choice and change the constants GPIO_PIN_x.')	
		elif mode == 'd':
			LEDC.disco_mode()	
			LEDC.stop()	
		elif mode == 'r':
			LEDC.raupe()	
			LEDC.stop()	
		elif mode == 't':
			LEDC.progress_mode()	
			LEDC.stop()	
		
	if switch_to_joy:
		if program_start_dialog() == 'j':
			joy = xbox.Joystick()
			joystick_mainloop(joy, LEDC)
		
		
def joystick_mainloop(joy, LEDC):
	switch_to_key = 0
	current_led = -1 % LED_COUNT	
	simple_game_speed = 1
	while 1:
		if joy.Back():
			# Close application.
			joy.close()
			break
		elif joy.dpadDown():
			# Switch to keyboard input style.
			switch_to_key = 1
			break
		elif joy.dpadUp():
			# Show all functions and print their names to console.
			LEDC.show_off()
		elif joy.dpadRight():
			# Switch to the next LED.
			current_led = (current_led + 1) % 4
			LEDC.phase([current_led], 0.3)
			LEDC.stop()
		elif joy.dpadLeft():
			# Switch to the previous LED.
			current_led = (current_led - 1) % 4
			LEDC.phase([current_led], 0.3)
			LEDC.stop()
		elif joy.leftTrigger():
			# Let the current LED blink.
			LEDC.blink([current_led], 1.01-joy.leftTrigger())							
		elif joy.rightBumper():
			# Increase game speed.
			simple_game_speed = (simple_game_speed + 1) % 4	
			LEDC.blink(list(range(simple_game_speed+1)), delay1=0.5, delay2=0.001, rounds=1)		# If delay2=0, then delay2=delay1... not what we want.				
		elif joy.leftBumper():
			# Decrease game speed.
			simple_game_speed = (simple_game_speed - 1) % 4
			LEDC.blink(list(range(simple_game_speed+1)), delay1=0.5, delay2=0.001, rounds=1)
		elif joy.Start():
			# Start the simple game.
			sg = SimpleGame(LEDController, GAME_SPEED_RECIPROCALS[simple_game_speed])
			print("Score: " + str(sg.run()))
			
		inpt = [joy.A(), joy.B(), joy.X(), joy.Y()]
		LEDC.phase([i for i in range(4) if inpt[i]])
		
		#x, y = joy.leftStick()
		#angle, radius = polar_coords(x,y)
		time.sleep(MAIN_LOOP_DELAY)
	
	if switch_to_key:
		joy.close()
		keyboard_mainloop(LEDC)

def program_start_dialog():
	try:
		import xbox
		input_mode = 'j'
	except:
		#raise
		#print('Cannot import xbox script. \nPress "h" for solutions.')
		input_mode = raw_input("Chose input...\nj - gamepad \nk - keyboard \nInput: ")
	return input_mode

			
			
if __name__ == '__main__':
	
	LEDController = LedControllerBase(GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3, GPIO_PIN_4)  
	print("Initialized led-controller")
	
	input_mode = program_start_dialog()
	
	if input_mode == 'j':
		joy = xbox.Joystick()
		joystick_mainloop(joy, LEDController)	

	elif input_mode == 'k':
		keyboard_mainloop(LEDController)
				
	print("Goodbye")			
	LEDController.stop()
	GPIO.cleanup()		
