from __future__ import print_function

import RPi.GPIO as GPIO
import time
import math
import random
from itertools import chain, combinations


# 1 Global Constants
# Feel free to adjust them to your needs. You may specify more or less than 
# four GPIO Pins. GPIO_PIN_1 should be the LED furthest to the left. GPIO_PIN_2 
# should be the LED next to the first one, and so on.

# 1.1 GPIO related
GPIO_PIN_NUMBER_MODE = 1 # 1 for GPIO.BCM, 0 for the other
GPIO_PIN_1 = 16
GPIO_PIN_2 = 5
GPIO_PIN_3 = 25
GPIO_PIN_4 = 22

# 1.2 Game related
GAME_SHOW_DELAY = 0.5
GAME_INPUT_DELAY = 0.25
# 1.2.1 Led Memory
GAME_SPEED_RECIPROCALS = [0.75, 1, 1.35, 1.8]
# 1.2.2 Hau den Lukas
TIME_DECREASE_TABLE = [2, 1.5, 1.25, 1, 0.9, 0.8, 0.75, 0.7, 0.6, 0.5, 0.45, 0.4]

# 1.3 Miscellaneous
INPUT_LOOP_DELAY = 0.001
STD_DELAY = 0.3



class LedControllerBase():
	def __init__(self, *args):
		self.pins = [a for a in args]
		self.led_indices = list(range(len(self.pins)))
		self.post_init()
		
	def post_init(self):
		# Call GPIO pins via their number.
		GPIO.setmode(GPIO.BCM)

		# Set directions of pins.
		for p in self.pins:
			GPIO.setup(p, GPIO.OUT)
		
	def phase(self, code, delay=0):		
		""" Light up all specified LEDs.
			<code> is a list of numbers corresponding to the indices of the list self.pins, 
			i.e. 1 correspondes to the LED plugged to GPIO_PIN_2 """
		status = [GPIO.HIGH if self.pins.index(p) in code else GPIO.LOW for p in self.pins]
		map(lambda a: GPIO.output(*a), zip(self.pins, status))
		time.sleep(delay)
			
		
	def test(self):
		for i in range(len(self.pins)):
			self.blink([i], STD_DELAY)
		self.stop()
		return time.time
		
			
	def blink(self, code, delay1=STD_DELAY, delay2=0, rounds=1):
		for i in range(rounds):
			self.phase(code)
			time.sleep(delay1)
			self.stop()
			time.sleep(delay2 if delay2 else delay1)
		return time.time
		
		
	def disco_mode(self, rounds=100):
		comb = list(chain.from_iterable(combinations(self.led_indices, r) for r in range(len(self.led_indices))))
		#comb = [[], [0], [1], [2], [3], [0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3], [0, 1, 2], [1, 2, 3], [0, 2, 3], [0, 1, 3]] for 4 pins
		for i in range(rounds):
			s = random.random()				
			self.phase(random.choice(comb))
			time.sleep(0.2*s)
		self.stop()
		return time.time
		
	
	def raupe(self, delay=STD_DELAY, rounds=20, rev=False):
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


class BinaryCalculator():
	""" Four LEDs are perfectly suited to show the binary numbers between 0001 and 1111. 
		This class lets you calculate on this set of numbers.
	"""
	def __init__(self, led_controller, joystick):
		self.LEDC = led_controller
		self.joy = joystick
		self.binary_number = [[], [0], [1], [0, 1], [2], [0,2], [1,2], [0,1,2], [3], [0,3], [1,3], [0,1,3], [2,3], [0,2,3], [1,2,3], [0,1,2,3]]
		# Example: 7 = 1 + 2 + 4 = 2^0 * 2^1 * 2^2 = [0, 1, 2]
		self.current_number = 0 # decimal system, i.e. corresponds to indices of self.binary_numbers
	
	def str_op(self, op):
		if op == 0:
			op = '+'
		elif op == 1:
			op = '-'
		elif op == 2:
			op = '*'
		elif op == 3:
			op = '/'
		return op
		
	def str_num(self, num):
		if num < 10:
			num = ' {}'.format(num)
		else:
			num = str(num) 
		return num
		
	def calculate(self, a, b, op):
		N = len(self.binary_number)
		if op == 0:
			c = a + b 
		elif op == 1:
			c =  a - b
		elif op == 2:
			c =  a * b
		elif op == 3:
			c =  a/b
		c = c%N
		return c
		
	def change_current_number(self, direction):
		ledc = self.LEDC
		joy = self.joy
		N = len(self.binary_number)
		old_number = self.current_number
		start_time = time.time()
		#delay = abs(self.current_number - old_number) 
		delay = 0
		while joy.rightTrigger() or joy.leftTrigger():
			ledc.phase(self.binary_number[self.current_number])
			if time.time() > start_time + delay:
				if direction > 0:
					self.current_number = (self.current_number + 1) % N
				elif direction < 0:
					self.current_number = (self.current_number - 1) % N
				delay += (1.05 - joy.rightTrigger() - joy.leftTrigger())
			time.sleep(INPUT_LOOP_DELAY)
			
	def run(self):
		joy = self.joy
		ledc = self.LEDC
		print("Starting Binary Calculator...")
		ledc.progress_mode()
		ledc.stop()
		print("Controls:")
		print("A            - +\nB            - -\nX            - *\nY            - /\nRightBumper  - =\nRightTrigger - next binary number\nLeftTrigger  - previous binary number\nBack         - +\n")
		a = -1
		b = -1
		op = -1
		pick = []
		while 1:
			# Enter a number and confirm with a A, B, X, Y or LeftBumper.
			ledc.phase(self.binary_number[self.current_number])
			if joy.Back():
				print("Closing Binary Calculator...")
				ledc.progress_mode(inv=True)
				return True
			if joy.rightTrigger():					
				# Switch to the next binary at the given speed
				self.change_current_number(1)
			if joy.leftTrigger():
				self.change_current_number(-1)
			if joy.rightBumper():
				if not a<0:
					b = self.current_number
					print(" {}".format(self.str_num(b)))
					print("----")
					c = self.calculate(a, b, op)
					print("= {}".format(self.str_num(c))) 
					self.current_number = c
					a, b, op = [-1]*3
					pick = []
					print()
										
			inpt = [joy.A(), joy.B(), joy.X(), joy.Y()]
			pick = [inpt.index(el) for el in inpt if el] if not pick else pick
			if pick:
				
				ledc.blink([0,1,2,3], rounds=2) # alternative: time.sleep(0.2), to prevent the pick from being fired again and again
				
				if a<0:
					a = self.current_number
					op = pick[0]
					print("  {}".format(self.str_num(a)))
					print("{}".format(self.str_op(op)), end="")
					
				elif b<0:
					b = self.current_number
					a = self.calculate(a, b, op)
					print(" {}".format(self.str_num(b)))
					print("= {}".format(self.str_num(a)))
					self.current_number = a					
					op = pick[0]
					print("{}".format(self.str_op(op)), end="")
					b = -1	
				pick = []			
			time.sleep(INPUT_LOOP_DELAY)
			
			

class LedMemory():
	""" Starting with three, each round LEDs 
		will light up. The player has to memorize in which order the LEDs light up. 
		After the sequence is shown, the player has to repeat it using the gamepad 
		buttons A, B, X and Y. If the sequence was repeated correctly, you will get 
		a new sequence with one more LED lighting up. """
	def __init__(self, led_controller, joystick, speed):
		self.LEDC = led_controller
		self.joy = joystick
		self.speed_factor = 1/GAME_SPEED_RECIPROCALS[speed]
		
	def forge_sequence(self, lngth):
		seq=[]
		for i in range(lngth):
			p = random.choice(self.LEDC.pins)
			seq.append(self.LEDC.pins.index(p))
		return seq
		
	def show_sequence(self, seq):
		for s in seq:
			self.LEDC.blink([s], delay1=self.speed_factor * GAME_SHOW_DELAY, delay2=self.speed_factor * 0.33 * GAME_SHOW_DELAY)
			
	def run(self):
		""" Governs the game process. """
		print("Starting Led Memory...")
		self.LEDC.progress_mode()
		self.LEDC.stop()
		print("Controls:")
		print("A    - LED 1\nB    - LED 2\nX    - LED 3\nY    - LED 4\nBack - close game\n")
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
					print("Closing Led Memory...")
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
				time.sleep(INPUT_LOOP_DELAY)
										
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
		mode = raw_input("Command: ")
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
			LEDC.show_off()	
			LEDC.stop()	
		elif mode == 'p':
			LEDC.progress_mode()	
			LEDC.stop()	
		elif mode == 'h':
			print("Menu\n====\nx - quit\nj - switch to gamepad control\ns - change GPIO pin numbers\nd - disco mode\nr - raupe\nt - test mode\np - progress mode")
		
	if switch_to_joy:
		input_mode, joy = start_routine()
	
		if input_mode == 'j':
			joystick_mainloop(joy, LEDController)	
		elif input_mode == 'k':
			keyboard_mainloop(LEDController)
		
def joystick_mainloop(joy, LEDC):
	switch_to_key = 0
	current_led = 0 % len(LEDC.pins)	
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
			if current_led == 0:
				sg = LedMemory(LEDController, joy, simple_game_speed)
				print("Score: " + str(sg.run()))
			elif current_led == 1:
				sg = BinaryCalculator(LEDController, joy)
				sg.run()
			
		inpt = [joy.A(), joy.B(), joy.X(), joy.Y()]
		LEDC.phase([i for i in range(4) if inpt[i]])
		
		#x, y = joy.leftStick()
		#angle, radius = polar_coords(x,y)
		time.sleep(INPUT_LOOP_DELAY)
	
	if switch_to_key:
		keyboard_mainloop(LEDC)


def determine_input_mode():
	""" If xboxdrv was installed correctly, this will automatically chose 
		gamepad as your input device. Falls back to keyboard input style otherwise. """
	try:
		print("Importing xbox python module...")
		global xbox
		import xbox
		return 'j'
	except ImportError:
		print('Cannot import xbox script. Maybe xboxdrv is missing.')
	return 'k'

def connect_gamepad():
	""" If no gamepad can be found, it falls back to keyboard input style. """
	try:
		print("Connecting the gamepad...")
		return xbox.Joystick()
	except IOError:
		print("The gamepad cannot be found. Switching to keyboard input...")
		return 0			

def start_routine():
	""" Calls determine_input_mode() and connect_gamepad(). Returns the input_mode 
		and the joystick if one is connected. """
	input_mode = determine_input_mode()
	joy = connect_gamepad()
	
	if input_mode == 'j' and joy:
		print("GAMEPAD input style.")
		return 'j', joy			
	elif input_mode == 'k' or not joy:
		print("KEYBOARD input style.")
		return 'k', joy
			
if __name__ == '__main__':
	
	print("Starting...")
	LEDController = LedControllerBase(GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3, GPIO_PIN_4)  
	print("Initialized led-controller.")
	LEDController.raupe(rounds = 2, delay=0.1)
	
	input_mode, joy = start_routine()	
	if input_mode == 'j':
		joystick_mainloop(joy, LEDController)	
	elif input_mode == 'k':
		keyboard_mainloop(LEDController)
				
	print("Goodbye")		
	LEDController.raupe(rounds = 2, delay=0.1, rev = True)
	if joy:
		joy.close()		
	LEDController.stop()
	GPIO.cleanup()		
