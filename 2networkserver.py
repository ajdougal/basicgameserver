import time
import socket
import threading

players_model_dict = {"p1":{"name":"p1", "x":100, "y": 200}, "p2":{"name":"p2", "x":100, "y": 200}, "p3":{"name":"p3", "x":100, "y": 200},"p4":{"name":"p4", "x":100, "y": 200}, "p5":{"name":"p5", "x":100, "y": 200}, "p6":{"name":"p6", "x":100, "y": 200}, "p7":{"name":"p7", "x":100, "y": 200}, "p8":{"name":"p8", "x":100, "y": 200}}
players_outbound_dict = {"p1":{"name":"p1", "x":100, "y": 200}, "p2":{"name":"p2", "x":100, "y": 200}, "p3":{"name":"p3", "x":100, "y": 200},"p4":{"name":"p4", "x":100, "y": 200}, "p5":{"name":"p5", "x":100, "y": 200}, "p6":{"name":"p6", "x":100, "y": 200}, "p7":{"name":"p7", "x":100, "y": 200}, "p8":{"name":"p8", "x":100, "y": 200}}
players_inbound_dict = {"p1":{"name":"p1", "joyx":0, "joyy": 0}, "p2":{"name":"p2", "joyx":0, "joyy": 0}, "p3":{"name":"p3", "joyx":0, "joyy": 0},"p4":{"name":"p4", "joyx":0, "joyy": 0}, "p5":{"name":"p5", "joyx":0, "joyy": 0}, "p6":{"name":"p6", "joyx":0, "joyy": 0}, "p7":{"name":"p7", "joyx":0, "joyy": 0}, "p8":{"name":"p8", "joyx":0, "joyy": 0}}
players_networking = dict()
time1 = time.time()
time2 = time.time()
time.sleep(0.001)

speed = 50


class TCPHandshakeThread(object):
    def __init__(self, interval=0.1):
        self.interval = interval
        self.tcp_inbound_ip = "192.168.1.5"
        self.tcp_inbound_port = 10001
        self.tcp_buffer_size = 1024

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', self.tcp_inbound_port))
        self.s.listen(1)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = False
        thread.start()

    def run(self):
        while True:
            global players_networking
            conn, addr = self.s.accept()
            print ("Connection address:{}".format(addr))
            while 1:
                data = conn.recv(self.tcp_buffer_size)
                data_string = data.decode("utf-8")
                if not data: break
                split_message = data_string.split(";")
                players_networking[split_message[2]] = dict()
                players_networking[split_message[2]]["address"] = split_message[0]
                players_networking[split_message[2]]["port"] = split_message[1]
                print ("received data:{}".format(addr))
                conn.send(data)
            conn.close()

class NetworkingInboundThread(object):
    def __init__(self, interval=0.03):
        self.interval = interval

        self.in_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('192.168.1.5', 10000)
        self.in_sock.bind(self.server_address)



        thread = threading.Thread(target=self.run, args=())
        thread.daemon = False
        thread.start()

    def run(self):
        while True:
            global players_inbound_dict
            data, addr = self.in_sock.recvfrom(4096)
            print (addr)

            if data:
                try:
                    data_split = data.decode('utf-8').split(";")
                    players_inbound_dict[data_split[0]]['joyx'] = data_split[1]
                    players_inbound_dict[data_split[0]]['joyy'] = data_split[2]
                except:
                    print('error?')
            time.sleep(self.interval)

class NetworkingOutboundThread(object):
    def __init__(self, interval = 0.03):
        self.interval = interval
        self.out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('192.168.1.5', 10001)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            global players_outbound_dict, players_networking
            out_message = ""
            for player in players_outbound_dict:
                out_message = out_message + "{};{};{}:".format(players_outbound_dict[player]["name"], 
                    players_outbound_dict[player]["x"], players_outbound_dict[player]["y"])
            for client in players_networking:
                c = players_networking[client]
                self.out_sock.sendto(out_message.encode(), (c['address'], int(c['port'])))
            time.sleep(self.interval)

class MainGameThread(object):
    def __init__(self, interval=0.02):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            global players_model_dict, players_inbound_dict, players_outbound_dict, time1, time2, speed
            time1 = time.time()
            dt = time1 - time2
            time2 = time1

            for i in range(1, 9):
                ind = "p{}".format(i)
                joyx = float(players_inbound_dict[ind]['joyx'])
                joyy = float(players_inbound_dict[ind]['joyy'])
                currentx = float(players_model_dict[ind]['x'])
                currenty = float(players_model_dict[ind]['y'])

                #experimental anti-drift technology
                if joyx*joyx/1000 + joyy*joyy/1000 < 2000:
                    joyx = 0
                    joyy = 0

                newx = currentx + joyx * (1/32768) * dt * speed
                newy = currenty + joyy * (1/32768) * dt * speed

                #print (newx, newy)
                players_model_dict[ind]['x'] = newx
                players_outbound_dict[ind]['x'] = newx

                players_model_dict[ind]['y'] = newy
                players_outbound_dict[ind]['y'] = newy


            time.sleep(self.interval)

def main():
    inthread = NetworkingInboundThread()
    outthread = NetworkingOutboundThread()
    gamethread = MainGameThread()
    handshakethread = TCPHandshakeThread()

if __name__ == "__main__":
    main()