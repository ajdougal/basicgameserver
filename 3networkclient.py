import time
import socket
import threading
import pygame
import os
#import evdev
import evdev
from evdev import InputDevice, categorize, ecodes

gamepad = None

for path in evdev.list_devices():
    gamepad = InputDevice(path)
#creates object 'gamepad' to store the data
#gamepad = InputDevice('/dev/input/event5')

leftjoyx = 0
leftjoyy = 0

server_playerx = 200
server_playery = 200

client_joyx = 'none'
client_joyy = 'none'

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen_size_object = (SCREEN_WIDTH, SCREEN_HEIGHT)

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
                    leftjoyy = event.value

class NetworkingInboundThread(object):
    def __init__(self, interval=0.03):
        self.interval = interval

        self.in_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('192.168.1.5', 10010)
        self.in_sock.bind(self.server_address)



        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            global server_playerx, server_playery
            data, addr = self.in_sock.recvfrom(4096)
            print (addr)

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
    def __init__(self, interval = 0.03):
        self.interval = interval
        self.out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('192.168.1.5', 10000)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            global client_joyx, client_joyy, leftjoyx, leftjoyy
            client_joyx = leftjoyx
            client_joyy = leftjoyy
            out_message = 'p1;{};{}'.format(client_joyx, client_joyy)
            self.out_sock.sendto(out_message.encode(), self.server_address)
            time.sleep(self.interval)

class Player(pygame.sprite.Sprite):
    def __init__(self, starting_location=(100,100)):
        super().__init__()
        self.location = starting_location
        # self.player_image_surface = pygame.Surface((50,50))
        self.player_image = pygame.image.load("red_circle.png").convert()
        self.player_image_small = pygame.transform.scale(self.player_image, (50,50))

    def update(self):
        global server_playerx, server_playery
        self.location = (server_playerx, server_playery)
        self.playerx = int(float(server_playerx))
        self.playery = int(float(server_playery))



class PygameThread(object):
    def __init__(self, fps=60):
        self.fps = 60
        self.game_window = pygame.display.set_mode((screen_size_object))

        self.p1 = Player()
        self.all_players = pygame.sprite.Group()
        self.all_players.add(self.p1)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = False
        thread.start()

    def run(self):
        while True:
            # clear game window
            self.game_window.fill((255,255,255))

            for player in self.all_players:
                player.update()
                centerx = int(player.playerx)
                centery = int(player.playery)

                self.game_window.blit(player.player_image_small, (player.playerx, player.playery))
            pygame.display.update()
            pygame.time.Clock().tick(self.fps)



def main():
    inthread = NetworkingInboundThread()
    outthread = NetworkingOutboundThread()
    controllerthread = ControllerInputStreamThread()
    
    pygamethread = PygameThread()

def connect_to_server():
    TCP_IP = '192.168.1.5'
    TCP_PORT = 10001
    BUFFER_SIZE = 1024
    MESSAGE = "192.168.1.5;10010;pnum:p1".encode()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()

    print ("received data:{}".format(data))

if __name__ == "__main__":
    connect_to_server()
    main()