import threading
import socket
import struct
import time
import pickle
import sys
from socket import error as er
import errno


def output_recvfrom(sock,my_name):
    global servers
    while True:
        try:
            data = sock.recv(1024)
            if not data: break
            print(data.decode())
        except ConnectionResetError:
            servers.remove(sock.getpeername())
            server_addr = addservers(sock,0,1000,1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.connect(server_addr)
            sock.send(struct.pack('>bbhh', 2, 1, len(my_name), 0))
            sock.send(my_name.encode())


def addservers(sock,size,elapsed,type):
    global servers
    min_rtt = elapsed
    min_addr = None
    if type == 0:
        data = sock.recv(size)
        picklearray = pickle.loads(data)
        servers.extend(picklearray)
        servers = list(set(servers))
    else:
        picklearray = servers
    for address in picklearray:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect(address)
        start = time.time()
        sock.send(struct.pack('>bbhh', 5, 0, 0, 0))
        sock.recv(6)
        done = time.time()
        RTT = done - start
        print("RTT for server ", str(sock.getpeername()), ' : ', str(RTT))
        if RTT < min_rtt:
            min_addr = address
            min_rtt = RTT
        sock.close()
    return min_addr

my_ip = socket.gethostbyname(socket.gethostname())
ports = [3000, 3001, 3002, 3003, 3004]
servers = []
selected_port = ports[int(input("select port you want to connect from 0-4: "))]
server_addr = (my_ip, selected_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
my_name = input('Enter your name: ')
sock.connect(server_addr)
servers.append(server_addr)
# sock.send(struct.pack('>bbhh',2,1,len(my_name),0))
# sock.send(my_name.encode())
start = time.time()
sock.send(struct.pack('>bbhh',5,1,0,0))
sock.recv(6)
done = time.time()
elapsed = done-start
print("RTT for server ", str(sock.getpeername()), ' : ', str(elapsed))
# sock.send(struct.pack('>bbhh',6,0,0,0))
data = sock.recv(6)
v1, v2, v3, v4 = struct.unpack('>bbhh', data)
if v1 == 1:
    min_addr = addservers(sock, v3, elapsed,0)
sock.close()
if min_addr:
    server_addr = min_addr
print("connect to server: ", str(server_addr))
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.connect(server_addr)
sock.send(struct.pack('>bbhh',2,1,len(my_name),0))
sock.send(my_name.encode())

threading.Thread(target=output_recvfrom, args=(sock, my_name)).start()
for line in sys.stdin:
    msg = line.strip()
    recipient = msg.split()[0]
    sock.send(struct.pack('>bbhh', 3, 0, len(msg), len(recipient)))
    sock.send(msg.encode())

sock.close()
x.join()
