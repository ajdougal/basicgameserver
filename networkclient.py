import time
import socket
import threading
import arcade
import os
#import evdev
from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
gamepad = InputDevice('/dev/input/event5')

leftjoyx = 0
leftjoyy = 0

server_direction = 'none'
client_direction = 'none'

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

MOVEMENT_SPEED = 5

SPRITE_SCALING = 0.25

class ControllerInputStreamThread(object):
    def __init__(self, interval= 0.02):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        global leftjoyx, leftjoyy
        for event in gamepad.read_loop():
             # event type 3 indicates an absolute axis event (joystick in our case) 
            if event.type == 3:
                # make sure it's a left joystick event (and not triggers/right joystick)
                # 0,1 are leftx/lefty
                # 2 is left trigger z
                # 3,4 are rightx/righty
                # 5 is right trigger z
                if event.code == 0:
                    leftjoyx = event.value
                elif event.code == 1:
                    leftjoyy = event.value

class NetworkingInboundThread(object):
    def __init__(self, interval=0.05):
        self.interval = interval

        self.in_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 10001)
        self.in_sock.bind(self.server_address)



        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            global server_direction
            data, addr = self.in_sock.recvfrom(4096)

            if data:
                print(data.decode('utf-8'))
                if data.decode('utf-8') == 'kill':
                    break
                elif data.decode('utf-8') == 'server_up':
                    server_direction = 'up'
                elif data.decode('utf-8') == 'server_down':
                    server_direction = 'down'
                elif data.decode('utf-8') == 'server_left':
                    server_direction = 'left'
                elif data.decode('utf-8') == 'server_right':
                    server_direction = 'right'
                elif data.decode('utf-8') == 'server_none':
                    server_direction = 'none'
                else:
                    print(data.decode('utf-8'))
            time.sleep(self.interval)

class NetworkingOutboundThread(object):
    def __init__(self, interval = 0.05):
        self.interval = interval
        self.out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 10000)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            global client_direction
            out_message = 'client_{}'.format(client_direction)
            self.out_sock.sendto(out_message.encode(), self.server_address)
            time.sleep(self.interval)

class Player(arcade.Sprite):

    def update(self):
        global server_direction, MOVEMENT_SPEED
        if server_direction == 'up':
            self.change_y = MOVEMENT_SPEED
            print ('uuuuup')
        elif server_direction == 'left':
            self.change_x = -1 * MOVEMENT_SPEED
            print ('leffffft')
        elif server_direction == 'down':
            self.change_y = -1 * MOVEMENT_SPEED
        elif server_direction == 'right':
            self.change_x = MOVEMENT_SPEED
        else:
            self.change_x = 0
            self.change_y = 0

        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.left < 0:
            self.left = 0
        if self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        if self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1

class MyApplication(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "DoogleSports DiscGame")

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.player_list = None
        self.player_sprite = None
        
        arcade.set_background_color(arcade.color.BLACK)
    
    def setup(self):
        self.player_list = arcade.SpriteList()

        self.player_sprite = Player("red_circle.png", SPRITE_SCALING)
        self.player_sprite.center_x = SCREEN_WIDTH/2
        self.player_sprite.center_y = SCREEN_HEIGHT/2
        self.player_list.append(self.player_sprite)


    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()

    def update(self, delta_time):
        self.player_list.update()
        global leftjoyx, leftjoyy
        print (leftjoyx, leftjoyy)


    def on_key_press(self, key, modifiers):
        global client_direction
        if key == arcade.key.UP:
            client_direction = 'up'
        elif key == arcade.key.DOWN:
            client_direction = 'down'
        elif key == arcade.key.LEFT:
            client_direction = 'left'
        elif key == arcade.key.RIGHT:
            client_direction = 'right'

    def on_key_release(self, key, modifiers):
        global client_direction
        if key == arcade.key.UP or key == arcade.key.DOWN:
            print('let go of up/down')
            client_direction = 'none'
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            print('let go of left/right')
            client_direction = 'none'

class ArcadeGameThread(object):
    def __init__(self):
        print ("Starting arcade")

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = False
        thread.start()

    def run(self):
        window = MyApplication(500, 500)
        window.setup()
        arcade.run()

def main():
    inthread = NetworkingInboundThread()
    outthread = NetworkingOutboundThread()
    controllerthread = ControllerInputStreamThread()
    
    window = MyApplication(500, 500)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()