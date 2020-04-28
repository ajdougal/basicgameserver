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

server_playerx = 0
server_playery = 0

client_joyx = 'none'
client_joyy = 'none'

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

MOVEMENT_SPEED = 5

SPRITE_SCALING = 0.1

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
                    leftjoyy = -1*event.value

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
            global server_playerx, server_playery
            data, addr = self.in_sock.recvfrom(4096)

            if data:
                try:
                    data_array = data.decode('utf-8').split(":")
                    player_array = data_array[0].split(";")
                    server_playerx = player_array[1]
                    server_playery = player_array[2]
                except:
                    print('error?')
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
            global client_joyx, client_joyy, leftjoyx, leftjoyy
            client_joyx = leftjoyx
            client_joyy = leftjoyy
            out_message = 'p1;{};{}'.format(client_joyx, client_joyy)
            print(out_message)
            self.out_sock.sendto(out_message.encode(), self.server_address)
            time.sleep(self.interval)

class Player(arcade.Sprite):

    def update(self):
        global server_playerx, server_playery
        self.center_x = float(server_playerx)
        self.center_y = float(server_playery)

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
        window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
        window.setup()
        arcade.run()

def main():
    inthread = NetworkingInboundThread()
    outthread = NetworkingOutboundThread()
    controllerthread = ControllerInputStreamThread()
    
    window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()