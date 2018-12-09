
Control LEDs plugged to a Raspberry Pi using a joystick/controller or your keyboard

Raspberry Pi
Breadboard
LEDs
Resistor 470R
Jumper Cable
XBox controller 


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

