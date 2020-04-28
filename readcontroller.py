#import evdev
from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
gamepad = InputDevice('/dev/input/event5')

#evdev takes care of polling the controller in a loop
for event in gamepad.read_loop():

    # event type 3 indicates an absolute axis event (joystick in our case) 
    if event.type == 3:
        # make sure it's a left joystick event (and not triggers/right joystick)
        # 0,1 are leftx/lefty
        # 2 is left trigger z
        # 3,4 are rightx/righty
        # 5 is right trigger z
        if event.code == 0:
            print ("Left Joystick X value is {}".format(event.value))
            print ("relatively it is : {}".format(event.value/32768))
        elif event.code == 1:
            print ("Left Joystick Y value is {}".format(event.value))
            print ("relatively it is : {}".format(event.value/32768))