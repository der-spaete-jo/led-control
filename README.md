# led-control

Control LEDs plugged to a Raspberry Pi using a gamepad/xbox-controller or 
your keyboard. If using a gamepad, you can access some simple games and programs.

## Led Memory 

Starting with three, each round LEDs will light up. 
The player has to memorize in which order the LEDs light up. 
When the sequence is shown, the player has to repeat it using the gamepad 
buttons A, B, X and Y. If the sequence was repeated correctly, you will get 
a new sequence with one more LED lighting up. 

## Binary Calculator

Lets you add and subtract in the space of integers modulo 16. Your input and 
the results are represented using the four LEDs. To read it, follow this 
algorithm:
```
n = 0
for i in range(4):
	if (LED i is on):
		n = n + 2**i
```
E.g.: If the LED furthest to the left and the LED furthest to the right are on, 
then n = 2^0 + 2^3 = 1 + 8 = 9. If both LEDs in the middle are on, then n = 
2^1 + 2^2 = 2 + 4 = 6. 

## Other Uses

This repo can also be a starting point for any other "control"-like project 
on the RPi, e.g. a robot.

# Components

 - Raspberry Pi

 - Breadboard

 - LEDs

 - Resistor 470R

 - Jumper Cable

 - XBox controller or comparable gamepad
 
 - USB-dongle if it is a wireless gamepad


# Installation

## Hardware

Use the image circuit.jpg to prepare the proper circuit. Double check it before 
plugging the jumper cables to your raspberry pi. 

## Software

Open a terminal on your RPi
```
sudo apt-get update
sudo apt-get install xboxdrv
```
Plug in the controller dongle and start the controller.
```
sudo xboxdrv --detach-kernel-driver
```
The values of the gamepad buttons are printed to console. Hit some buttons and 
verify that the console output adapts. If it does hit `Strc+c` to quit this test 
mode otherwise see e.g. [tutorials-raspberrypi](https://tutorials-raspberrypi.de) 
or the [FRC4564/Xbox](https://github.com/FRC4564/Xbox) repository for details 
and some problem solving. 

Go to your projects folder, clone or download this repository and cd into it.

```
cd ~/Projects
git clone https://github.com/der-spaete-jo/led-control  
cd led-control
sudo python lights.py
```

# Gamepad Control


## Main Menu

Back - close application

A - LED 1

B - LED 2

X - LED 3

Y - LED 4

Right Bumper - increase Led Memory game speed

Left Bumper - decrease Led Memory game speed

Start - start simple game

Left Trigger - blink current LED

DPAD Left - switch to next LED

DPAD Right - switch to previous LED

DPAD Up - show all predefined LED light patterns

DPAD Down - switch to keyboard input


## Led Memory

Back - close game

A - LED 1

B - LED 2

X - LED 3

Y - LED 4

### A Word Of Warning

After a Led Memory game started, gamepad commands will only be processed during the 
players "turn". This is True for A, B, X, Y, but most importantly also for 
the Back button. This means you cannot quit the game, when the game is  
showing you a sequence. (This is not a feature, but rather bad design.)

## Binary Calculator

Please start the program and refer to the console output. To start Binary 
Calculator, chose the second LED using DPAD Left and press the Start button 
on your gamepad. 


# Keyboard Control

Please start the script `python lights.py`, choose keyboard as your input mode 
and hit "h". Note that ommiting `sudo` in `sudo python lights.py` should 
automatically result in keyboard input style. 

# Issues

If the script is exited ungracefully (e.g. by an exception or hitting "str+c"), 
the gamepad may not work properly when restarting the script. 
To prevent this, always close the application with the back button 
(gamepad control) or by hitting "x" (keyboard control).
Solution: Unplug the controller and wait some seconds before plugging the 
dongle back in. Restart the script. If you are using a 'universal' gamepad 
(e.g. I am using Trust GXT 545) it might suffice to switch the input mode of 
the gamepad. To do this find the well hidden toggle switch on the back of the 
gamepad. Switch it to "D" and then back to "X".
 
When chosing gamepad control via the keyboard command "j", sometimes nothing 
happens. Just issue the command again in this case.

When closing the application with the Back button and then restarting it via 
```sudo python lights.py```, sometimes the game is closed instantly after 
starting. Just issue the command again in this case.

Switching between gamepad and keyboard input style is very buggy. 

# Thanks

Thanks to Steven Jacobs for his xbox python module FRC4564/Xbox. 
Thanks to Felix at [tutorials-raspberrypi](https://tutorials-raspberrypi.de) for his wonderful tutorials 
which encuraged me to buy a RPi and are a great source for inspiration.
