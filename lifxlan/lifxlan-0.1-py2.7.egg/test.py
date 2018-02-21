from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST
from message import BROADCAST_MAC, BROADCAST_SOURCE_ID
from msgtypes import *
from unpack import unpack_lifx_message
 
UDP_BROADCAST_IP = "255.255.255.255"
UDP_BROADCAST_PORT = 56700

def send_broadcast_msg(msg):
	sock = socket(AF_INET, SOCK_DGRAM)
	sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	port = UDP_BROADCAST_PORT
	sock.bind(("", port))
	print "waiting on port:", port
	sent = False
	while 1:
		if sent == False:
			print("\nSENT:"),
			#print([hex(b) for b in struct.unpack("B"*(len(msg.packed_message)),msg.packed_message)]) # TEST
			print(str(msg))
			print("\n")
			sock.sendto(msg.packed_message, (UDP_BROADCAST_IP, UDP_BROADCAST_PORT))
			sent = True
		data, addr = sock.recvfrom(1024)
		print("RECV:"),
		#print([hex(b) for b in struct.unpack("B"*(len(data)),data)])
		response = unpack_lifx_message(data)
		if response != None:
			print(response)
		else:
			print("Unimplemented message")
		print("\n")
		#print(response)

def test_broadcast():
	#my_source_id = 1000239
	#m = GetService(BROADCAST_MAC, BROADCAST_SOURCE_ID, seq_num=0)	
	#m = SetPower(BROADCAST_MAC, BROADCAST_SOURCE_ID, seq_num=0, power_level=65535)	
	#m = LightSetColor(BROADCAST_MAC, BROADCAST_SOURCE_ID, seq_num=0, color=[10000, 10000, 65535, 9000], duration=1)	
	#m = LightSetPower(BROADCAST_MAC, BROADCAST_SOURCE_ID, seq_num=0, power_level=65535, duration=1000)
	#m = LightGetPower(BROADCAST_MAC, BROADCAST_SOURCE_ID, seq_num=1)
	#m = LightGet(BROADCAST_MAC, BROADCAST_SOURCE_ID, seq_num=1)
	m = GetPower(BROADCAST_MAC, BROADCAST_SOURCE_ID, seq_num=1, ack_requested=True)
	#m = SetLabel(BROADCAST_MAC, BROADCAST_SOURCE_ID, seq_num=0, label="Lotus Lamp")
	send_broadcast_msg(m)

test_broadcast()