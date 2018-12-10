
Control LEDs plugged to a Raspberry Pi using a gamepad/xbox-controller or your keyboard.
If using a gamepad, you can access a simple game.

Components
Raspberry Pi
Breadboard
LEDs
Resistor 470R
Jumper Cable
XBox controller 

Installation

Hardware
Use the image circuit.jpg to prepare the proper circuit. Double check it before plugging the jumper cables to your raspberry pi.


Software
Open a terminal on your RPi

sudo apt-get update
sudo apt-get install xboxdrv

Plug in the controller dongle and start the controller.

sudo xboxdrv --detach-kernel-driver

The values of the controller buttons are printed to console. 
Pressing controller buttons should show a response in the console.

Hit "Strc+c" to quit this test mode.

See raspberrypi-tutorials.de or the FRC4564/Xbox repository for details.

Clone or download this repository and cd into it.
  
cd led-control
sudo python lights.py

Gamepad Control

Main Menu
Back - close application
A - LED 1
B - LED 2
X - LED 3
Y - LED 4
Right Bumper - increase game speed
Left Bumper - decrease game speed
Start - start simple game
Left Trigger - blink current LED
DPAD Left - switch to next LED
DPAD Right - switch to previous LED
DPAD Up - show all predefined LED light patterns
DPAD Down - switch to keyboard input

Game Menu
Back - close game
A - LED 1
B - LED 2
X - LED 3
Y - LED 4

Issues

If the script is exited ungracefully (e.g. by an exception or hitting "str+c"), the gamepad may not work properly when restarting the script. 
To prevent this, always close the application with the back button (gamepad control) or by hitting "x" (keyboard control).
Solution: Unplug the controller and wait some seconds before plugging the dongle back in. Restart the script. If you are using a 'universal' gamepad (e.g. I am using Trust GXT 545) it might suffice to switch the input mode of the gamepad. To do this find the well hidden toggle switch on the back of the gamepad. Switch it to "D" and then back to "X".
 
When chosing gamepad control via the keyboard command "j", sometimes nothing happens. Just issue the command again in this case.

Thanks

Thanks to Steven Jacobs for his xbox python module FRC4564/Xbox. 
Thanks to Felix at Raspberri Pi Tutorials for his wonderful tutorials which encuraged me to buy a RPi and are a great source for inspiration.
