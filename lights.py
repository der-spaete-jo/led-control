import RPi.GPIO as GPIO
import time
import math
import random
from multiprocessing.dummy import Pool as ThreadPool 

import xbox



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
		for i in range(self.pins.length):
			self.phase([i])
			time.sleep(0.3)
			
	def blink(self, code, intervall=0.5):
		self.phase(code)
		time.sleep(intervall/2)
		self.stop()
		time.sleep(intervall/2)
	
	def disco_mode(self, rounds=100):
		print("DISCO")
		comb = [[0], [1], [2], [0, 1], [0, 2], [1, 2]]
		for i in range(rounds):
			s = random.random()				
			self.phase(random.choice(comb))
			time.sleep(0.2*s)
	
	def raupe(self, delay=0.15, rounds=20, rev=False):
		""" runtime: rounds*3*delay """
		for i in range(rounds):
			for j in range(3):
				self.phase([j]) if not(rev) else self.phase([2-j])
				time.sleep(delay)
				
	
	def progress_mode(self, delay=0.15, rounds=20, rev=False, inv=False):
		for i in range(rounds):
			for j in range(3):
				if inv:
					j = 2-j
				self.phase(list(range(j))) if not(rev) else self.phase([2-k for k in range(j)])
				time.sleep(delay)

			
	def crossway_mode(self, rounds=2):
		#pool = ThreadPool(4) 
		#results = pool.map(my_function, my_array)
		for i in range(rounds):
			self.phase(['2', '0'])
			time.sleep(5)
			self.phase(['2', '1'])
			time.sleep(1.5)
			self.phase(['21', '2'])
			time.sleep(1.5)
			self.phase(['0', '2'])
			time.sleep(5)
			self.phase(['1', '2'])
			time.sleep(1.5)
			self.phase(['2', '21'])
			time.sleep(1.5)
							
				
	def stop(self):
		""" All pins LOW """
		for p in self.pins:
			GPIO.output(p, GPIO.LOW)	


class SimpleGame():
	def __init__(self, led_controller):
		self.LEDC = led_controller
		
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
			self.LEDC.phase([s], 0.6)
			self.LEDC.stop()
			time.sleep(0.2)
			
	def run(self):
		self.LEDC.raupe(rounds=5)
		self.LEDC.stop()
		#time.sleep(1)
		N=3
		while 1:
			if joy.Back():
				time.sleep(0.2)
				break
			time.sleep(1)
			seq = self.forge_sequence(N)
			print(seq)
			self.show_sequence(seq)
			no = 0
			while not joy.Back():
				inpt = [joy.A(), joy.B(), joy.X()]
				pick = [inpt.index(el) for el in inpt if el]
				if pick:
					if len(pick)==1 and seq[no]==pick[0]:
						no=no+1
						#print(no)
						
					else: #any(inpt):
						print("You Lose")
						self.LEDC.disco_mode(rounds=20)
						return False
					
					self.LEDC.phase(pick, 0.3) #pick=[i for i in range(3) if inpt[i]]
					self.LEDC.stop()
					if no>=N:
						break
				time.sleep(0.001)
										
			N=N+1
		return True
			
	
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
			
if __name__ == '__main__':
	#sudo python ~/Documents/scipts/lights.py
	LEDController = LedControllerBase(5, 6, 12) #, 24, 23, 22 
	print("initialized traffic lights controller")
		
	input_mode = raw_input("Chose input...\nj - controller \nk - keyboard\n ")
	if input_mode == 'j':
		import xbox
		joy = xbox.Joystick()
		
		while 1:
			if joy.Back():
				joy.close()
				break
			if joy.Start():
				sg = SimpleGame(LEDController)
				sg.run()
				
			inpt = [joy.A(), joy.B(), joy.X(), joy.Y()]
			LEDController.phase([i for i in range(4) if inpt[i]])
			
			#x, y = joy.leftStick()
			#angle, radius = polar_coords(x,y)
			time.sleep(0.001)
		LEDController.stop()
		GPIO.cleanup()
			
	elif input_mode == 'k':
		while 1:
			mode = raw_input("Chose mode: ")
			if mode == 'n':
				LEDController.normal_mode()
				LEDController.stop()					
			elif mode == 'd':
				LEDController.disco_mode()	
				LEDController.stop()	
			elif mode == 'r':
				LEDController.raupe()	
				LEDController.stop()	
			elif mode == 't':
				tlc.progress_mode()	
				tlc.stop()	
			elif mode == 'x':			
				GPIO.cleanup()
				print("Strg + c to close program")
		
