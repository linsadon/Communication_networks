import threading
import socket
import struct
import sys


def output_recvfrom(sock):
    while True:
        data = sock.recv(1024)
        if not data: break
        print(data.decode())


my_ip = socket.gethostbyname(socket.gethostname())
ports = [3000, 3001, 3002, 3003, 3004]
selected_port = ports[int(input("select port you want to connect from 0-4: "))]
server_addr = (my_ip, selected_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
my_name = input('Enter your name: ')
sock.connect(server_addr)
sock.send(struct.pack('>bbhh',2,1,len(my_name),0))
sock.send(my_name.encode())

threading.Thread(target=output_recvfrom, args=(sock, )).start()
for line in sys.stdin:
    msg = line.strip()
    recipient = msg.split()[0]
    sock.send(struct.pack('>bbhh', 3, 0, len(msg), len(recipient)))
    sock.send(msg.encode())

sock.close()
x.join()
