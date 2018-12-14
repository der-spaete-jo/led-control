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
# 1.2.2 Another Game
TIME_DECREASE_TABLE = [1.25, 1.1, 0.9, 0.8, 0.75, 0.7, 0.6, 0.5, 0.45, 0.4, 0.3, 0.2, 0, 0, 0, 0]

# 1.3 Miscellaneous
INPUT_LOOP_DELAY = 0.01
STD_DELAY = 0.3
# The following constant is the smallest value x, that makes sense in
# ```	ledc.phase([...])
#		time.sleep(x - joystick.rightTrigger()) ```
# As rightTrigger is always <= 1, this is always >= 0.05. For smaller values, the  
# LED won't appear as blinking but as always on and dimmed.
NO_GOOD_NAME_CONSTANT = 1.05 


class LedControllerBase(object):
	def __init__(self, *args):
		self.pins = [a for a in args]
		self.led_indices = list(range(len(self.pins)))
		self.post_init()
		
	def post_init(self):
		# Call GPIO pins via their number.
		GPIO.setmode(GPIO.BCM)

		# Set direction and frequency of pins.
		for p in self.pins:
			GPIO.setup(p, GPIO.OUT)		
			
			
			
	def phase(self, code, delay=0):		
		""" Core method of the hole script: Light up all specified LEDs.
			<code> is a list of numbers corresponding to the indices of the list self.pins, 
			i.e. 1 correspondes to the LED plugged to GPIO_PIN_2 
		"""
		status = [GPIO.HIGH if self.pins.index(p) in code else GPIO.LOW for p in self.pins]
		map(lambda a: GPIO.output(*a), zip(self.pins, status))
		if delay:
			time.sleep(delay)
		
	def phase2(self, code, delay=0, independent=False, rev=False, inv=False, stop=False):		
		""" [skip this on first read] More sophisticated version of phase.
			If <independent> is True, LEDs not specified in code keep their state.
			If <rev> is True, LEDs specified in code, will be set to GPIO.LOW, i.e. 
			they will be turned off.
			If <inv> is True, code will be reset to all LEDs that are not in code.
			The difference between <inv> and <rev> is only visible when <independent>
			is set to True.
			
		"""
		status_A = GPIO.HIGH
		status_B = GPIO.LOW
		if rev:
			# , then interchange the stati.
			C = status_B
			status_B = status_A
			status_A = C
		if inv:
			# , then reset code to its difference with all pins.
			code = list(set(self.led_indices).difference(code))
			
		# Prepare list of lists, each holding a pin number and its desired status.
		if independent:
			status = [status_A for idx in code]
			pin_status = zip([p for p in self.pins if self.pins.index(p) in code], status)
		else:
			status = [status_A if self.pins.index(p) in code else status_B for p in self.pins]
			pin_status = zip(self.pins, status)
			
		# Set GPIO pin stati.
		map(lambda a: GPIO.output(*a), pin_status)
		# Optionally sleep and stop.
		if delay:
			time.sleep(delay)
		if stop:
			self.phase2(code, independent=independent, rev=True, inv=inv)
			
			
	def blink(self, code, rounds=1, delay1=STD_DELAY, delay2=-1):
		for i in range(rounds):
			self.phase(code, delay=delay1)
			self.stop()
			time.sleep(delay2 if delay2 >= 0 else delay1)
		return time.time()
		
		
	def phase_blink(self, code_phase, code_blink, delay=0, rounds=1, delay1=STD_DELAY, delay2=-1):
		self.phase(code_phase, delay=delay)
		delay2 = delay2 if delay2 >= 0 else delay1
		for i in range(rounds):
			self.phase2(code_blink, delay=delay1, independent=True)
			self.phase2(code_blink, delay=delay2, independent=True, rev=True)
	
	def start_pwm(self, code, freq=100):
		idx = code[0]
		pwm_pin = GPIO.PWM(self.pins[idx], freq)
		pwm_pin.start(0)
		return pwm_pin
		
	def dimm(self, pwm_pin, delay=0.1, freq=100, dc=50):
		# before a call to dimm: pwm_pin = self.start_pwm(code=code, freq=freq)	
		pwm_pin.ChangeDutyCycle(dc)
		time.sleep(delay)
		# after the call: self.stop_pwm(pwm_pin)
		
	def stop_pwm(self, pwm_pin):
		pwm_pin.stop()
		GPIO.cleanup()
		self.post_init()
				
	def disco_mode(self, rounds=100):
		""" Chose a subset of all pin indices randomly and phase them for 
			a random amount of time.
		"""
		comb = list(chain.from_iterable(combinations(self.led_indices, r) for r in range(len(self.led_indices))))
		#comb = [[], [0], [1], [2], [3], [0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3], [0, 1, 2], [1, 2, 3], [0, 2, 3], [0, 1, 3]] for 4 pins
		for i in range(rounds):
			s = random.random()	
			code = random.choice(comb)		
			self.phase(code, 0.2*s)
		self.stop()
		return time.time()
		
	
	def raupe(self, delay=STD_DELAY, rounds=20, rev=False):
		""" 
			Runs through all LEDs from left to right. Switches one LED on 
			at a time. After a delay it advances to the next LED, turning the 
			previous one off and the next one on.
			<rev> ... from right to left
		"""
		pc = len(self.pins)
		for i in range(rounds):
			for j in range(pc):
				self.phase([j]) if not(rev) else self.phase([pc-j-1])
				time.sleep(delay)
		self.stop()
		return time.time()
						
	
	def progress_mode(self, delay=0.3, rounds=1, rev=False, inv=False):
		""" This memes a progress bar 
			Successively switch on LEDs from left to right
			<rev> ... from right to left
			<inv> Successively switch off LEDs
		"""
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
		return time.time()
		
		
	def stop(self):
		""" All pins LOW 
			Equivalent to self.phase2(self.pins, rev=True)
		"""
		for p in self.pins:
			GPIO.output(p, GPIO.LOW)
	
	# More ideas for blinking patterns:
	# 	alternate blink: code1, code2 -> alternate phase(code1) and phase(code2)
	#	beat/disco: blink with a given bpm
	
	
	def test(self):
		print("Showing all modes")
		delay=0.5
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
	

class LedGameController(LedControllerBase):
	def __init__(self, *args):
		super(LedGameController, self).__init__(*args)

class LedPatternRepeater(object):
	""" Create a pattern and show it.
	"""
	def __init__(self, led_controller, joystick):
		self.LEDC = led_controller
		self.joy = joystick
		self.pattern = []
		
	def show_pattern(self):
		for pat in self.pattern:
			self.LEDC.phase2(pat[0], delay=pat[1], independent=True)
		self.LEDC.stop()
		
	def define_pattern(self):
		print("Please define your new pattern by pressing A, B, X and Y buttons")
		ledc, joy = self.LEDC, self.joy
		pattern = []
		change_pick = []
		start_pause = time.time()
		while 1:
			
			if self.joy.Back():
				self.pattern = pattern
				print("Saved new pattern:")
				print(self.pattern)
				ledc.progress_mode()
				return
			
			inpt = [joy.A(), joy.B(), joy.X(), joy.Y()]
			pick = [inpt.index(el) for el in inpt if el]
			
			ledc.phase2(pick, independent=True)					
					
			if pick:
				print(pick)
				end_pause = time.time()
				pattern.append([[], end_pause-start_pause])
				start_time = time.time()
				while 1:
					change_inpt = [joy.A(), joy.B(), joy.X(), joy.Y()]
					change_pick = [change_inpt.index(el) for el in change_inpt if el]
					
					if change_pick != pick:
						if change_pick:
							ledc.phase2(change_pick, independent=True)
						else:
							ledc.stop()
						print(change_pick)
						end_time = time.time()
						pattern.append([pick, end_time-start_time])
						start_pause = time.time()
						break
					time.sleep(INPUT_LOOP_DELAY)
		
			time.sleep(INPUT_LOOP_DELAY) 
		
	def run(self):
		
		ledc, joy = self.LEDC, self.joy
		ledc.progress_mode()
		time.sleep(0.5)
		while 1:
			if self.joy.Back():
				ledc.progress_mode(inv=True)
				return
			
			elif self.joy.dpadDown():
				self.define_pattern()
				
			elif self.joy.dpadUp():
				if self.pattern:
					self.show_pattern()
				else:
					self.LEDC.test()
					
			time.sleep(INPUT_LOOP_DELAY)
		
	
class AnotherGame():
	""" Each round is composed of five turns. In each turn, after a random time, 
		one of the LEDs will light up. The player then has a certain amount of time, 
		to press the gamepad button that corresponds to the LED. In each round the maximum response 
		time for the player is decreased by a thenth of a second. 
	"""
	def __init__(self, led_controller, joystick):
		self.LEDC = led_controller
		self.joy = joystick
		self.turns_per_round = 4
		self.time_decrease_table = TIME_DECREASE_TABLE
	
	def forge_sequence(self):
		seq=[]
		pause = []
		for i in range(self.turns_per_round):
			p = random.choice(self.LEDC.led_indices)
			seq.append(p)
			q = 0.3 + random.random() * 5
			pause.append(q)
		return zip(seq, pause)
	
		
	def run(self):
		
		ledc, joy = self.LEDC, self.joy
		N = 0
		ledc.progress_mode()
		time.sleep(0.5)
		while 1:			
			seq_pause = self.forge_sequence()
			ledc.blink(ledc.led_indices, rounds=N)
			time.sleep(0.5)
			for t in range(self.turns_per_round):
				secret, pause = seq_pause[t]
				checked = False
				#old_pick = 0
				pick = []
				ledc.blink(list(range(t+1)), rounds=3)
				ledc.stop()
				time.sleep(pause)
				ledc.phase([secret])
				start_time = time.time()
				while 1:
					# responding turn
					# wait for input, if any show it. If gamepad button is released, check the guess.
					if self.joy.Back():
						ledc.progress_mode(inv=True)
						return N
				
					if time.time() > start_time + TIME_DECREASE_TABLE[N] + 0.25:						
						print("Time is up!")
						ledc.disco_mode(rounds=20)
						return N
												
					inpt = [joy.A(), joy.B(), joy.X(), joy.Y()]
					pick = [inpt.index(el) for el in inpt if el] if not pick else pick #old_pick == pick else old_pick
					
					ledc.phase2(pick, independent=True)					
							
					if pick and not checked and not any([joy.A(), joy.B(), joy.X(), joy.Y()]):
						print(str(pick[0]), end=", ")
						checked = True
						if len(pick)==1 and secret==pick[0]:
							checked = False
							pick = []
							break
						else:
							ledc.phase_blink([secret], [pick[0]], rounds=5)							
							print("You Lose")
							self.LEDC.disco_mode(rounds=20)
							return N
					
					#old_pick = pick
					time.sleep(INPUT_LOOP_DELAY)
				
				ledc.stop()
			print()
			N = N+1
				
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
				delay += (NO_GOOD_NAME_CONSTANT - joy.rightTrigger() - joy.leftTrigger())
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
			self.LEDC.blink([s], delay1=self.speed_factor * GAME_SHOW_DELAY, delay2=self.speed_factor * GAME_SHOW_DELAY)
			
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
			LEDC.test()	
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
		
def joystick_mainloop(ledc, joy):
	switch_to_key = 0
	current_led = 0 % len(ledc.pins)	
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
			ledc.test()
		elif joy.dpadRight():
			# Switch to the next LED.
			current_led = (current_led + 1) % len(ledc.pins)
			ledc.phase([current_led], 0.3)
			ledc.stop()
		elif joy.dpadLeft():
			# Switch to the previous LED.
			current_led = (current_led - 1) % len(ledc.pins)
			ledc.phase([current_led], 0.3)
			ledc.stop()
		elif joy.leftTrigger():
			# Let the current LED blink.
			ledc.blink([current_led], delay1=0.5*(NO_GOOD_NAME_CONSTANT-joy.leftTrigger()))							
		elif joy.rightTrigger():
			# Dimm the current LED.
			old_led = current_led
			pwm_pin = ledc.start_pwm([current_led], 50)
			while 1:
				ledc.dimm(pwm_pin, dc=100*joy.rightTrigger())
				if joy.rightTrigger()<0.05:
					ledc.stop_pwm(pwm_pin)
					ledc.stop()
					break
			current_led = old_led
		elif joy.rightBumper():
			# Increase game speed.
			simple_game_speed = (simple_game_speed + 1) % len(GAME_SPEED_RECIPROCALS)	
			ledc.blink(list(range(simple_game_speed+1)), delay1=0.5, delay2=0, rounds=1)				
		elif joy.leftBumper():
			# Decrease game speed.
			simple_game_speed = (simple_game_speed - 1) % len(GAME_SPEED_RECIPROCALS)
			ledc.blink(list(range(simple_game_speed+1)), delay1=0.5, delay2=0, rounds=1)
		elif joy.Start():			
			if current_led == 0:
				sg = LedMemory(ledc, joy, simple_game_speed)
				print("Score: " + str(sg.run()))
			elif current_led == 1:
				sg = BinaryCalculator(ledc, joy)
				sg.run()			
			elif current_led == 2:
				sg = AnotherGame(ledc, joy)
				print("Score: " + str(sg.run()))
			elif current_led == 3:
				sg = LedPatternRepeater(ledc, joy)
				sg.run()
				
		inpt = [joy.A(), joy.B(), joy.X(), joy.Y()]
		ledc.phase([i for i in range(4) if inpt[i]])
		
		#x, y = joy.leftStick()
		#angle, radius = polar_coords(x,y)
		time.sleep(INPUT_LOOP_DELAY)
	
	if switch_to_key:
		keyboard_mainloop(ledc)


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
		and the joystick if one is connected. 
	"""		
	print("Starting...")
	ledc = LedControllerBase(GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3, GPIO_PIN_4)  
	print("Initialized led-controller.")
	ledc.raupe(rounds = 2, delay=0.1)
		
	input_mode = determine_input_mode()
	joy = connect_gamepad()
	
	if input_mode == 'j' and joy:
		print("GAMEPAD input style.")
		return 'j', ledc, joy			
	elif input_mode == 'k' or not joy:
		print("KEYBOARD input style.")
		return 'k', ledc, joy
	
def exit_routine(ledc, joy):
	print("Goodbye")	
	if joy:
		joy.close()		
	ledc.stop()
	GPIO.cleanup()		

			
if __name__ == '__main__':
	
	input_mode, ledc, joy = start_routine()
	try:
		if input_mode == 'j':
			joystick_mainloop(ledc, joy)	
		elif input_mode == 'k':
			keyboard_mainloop(ledc)
	except KeyboardInterrupt, SystemExit:			
		exit_routine(ledc, joy)		
	
	ledc.raupe(rounds = 2, delay=0.1, rev = True)
	exit_routine(ledc, joy)
