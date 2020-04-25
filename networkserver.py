import time
import socket
import threading

player_direction = 'none'
player_direction = 'none'

class NetworkingInboundThread(object):
	def __init__(self, interval=0.05):
		self.interval = interval

		self.in_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server_address = ('localhost', 10000)
		self.in_sock.bind(self.server_address)



		thread = threading.Thread(target=self.run, args=())
		thread.daemon = False
		thread.start()

	def run(self):
		while True:
			global player_direction
			data, addr = self.in_sock.recvfrom(4096)

			if data:
				print(data.decode('utf-8'))
				if data.decode('utf-8') == 'kill':
					break
				elif data.decode('utf-8') == 'client_up':
					player_direction = 'up'
				elif data.decode('utf-8') == 'client_down':
					player_direction = 'down'
				elif data.decode('utf-8') == 'client_left':
					player_direction = 'left'
				elif data.decode('utf-8') == 'client_right':
					player_direction = 'right'
				elif data.decode('utf-8') == 'client_none':
					player_direction = 'none'
				else:
					print(data.decode('utf-8'))
			time.sleep(self.interval)

class NetworkingOutboundThread(object):
	def __init__(self, interval = 0.1):
		self.interval = interval
		self.out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server_address = ('localhost', 10001)

		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True
		thread.start()

	def run(self):
		while True:
			global player_direction
			out_message = 'server_{}'.format(player_direction)
			self.out_sock.sendto(out_message.encode(), self.server_address)
			time.sleep(self.interval)

def main():
	inthread = NetworkingInboundThread()
	outthread = NetworkingOutboundThread()

if __name__ == "__main__":
	main()