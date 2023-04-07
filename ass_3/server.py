import socket
import threading
import pickle
import json
import time
import struct

#('192.168.241.1', 3000)
serversdict=[]
clientsdict={}

def addservers(sock):
    pass

def createheader(t,st,l,sl):
    return struct.pack('>bbhh',t,st,l,sl)

def pingallusers():
    socket_objects = []
    global serversdict
    for address in serversdict:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((my_ip, my_port))
        sock.connect(address)
        socket_objects.append(sock)
        sock.close()
    # for sock in socket_objects:
    #     sock.send("conn try".encode())
    # for sock in socket_objects:
    #     sock.close()

def senddict(conn):
    global serversdict
    picklearray = pickle.dumps(serversdict)
    print(len(picklearray))
    conn.send(createheader(1, 0, len(picklearray), 0))
    conn.sendall(picklearray)

def acceptconnection(sock):
    while True:
        conn, client_address = sock.accept()
        print('new connection from', client_address)
        global serversdict
        if client_address not in serversdict:
            serversdict.append(client_address)
        # conn.close()
        # print("my list : " + str(serversdict))
        #threading.Thread(target=respond_to_client, args=(conn, client_address)).start()
        respond_to_client(conn, client_address)


def respond_to_client(conn_socket, client_address):
    # while True:
    # 0-----1-----2----------4----------6
    # |type | sub |    len   |   sub    |
    # |     |type |          |   len    |
    data = conn_socket.recv(6)
    if len(data)==0:
        conn_socket.close()
        return
    v1,v2,v3,v4 = struct.unpack('>bbhh',data)
    if v1 == 0:
        print("im sending dict")
        senddict(conn_socket)
    elif v1 == 1:
        pass
    conn_socket.close()


my_ip = socket.gethostbyname(socket.gethostname())
ports = [3000, 3001, 3002, 3003, 3004]
my_port = ports[int(input("select your port from 0-4: "))]
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((my_ip, my_port))
sock.listen(5)
threading.Thread(target=acceptconnection, args=(sock,)).start()
for i in ports:
    try:
        if i != my_port:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((my_ip, my_port))
            sock.connect((my_ip, i))
            # sock.send(str(input("enter your name : ")).encode())
            ###################################################
            #0-----1-----2----------4----------6
            #|type | sub |    len   |   sub    |
            #|     |type |          |   len    |
            sock.send(createheader(0,0,0,0))
            data = sock.recv(6)
            v1,v2,v3,v4 = struct.unpack('>bbhh',data)
            if v1 == 1:
                data = sock.recv(v3)
            picklearray = pickle.loads(data)
            print(picklearray)
            ###################################################
            #print('received from ', sock.getpeername(), sock.recv(1024).decode())
            serversdict.append(sock.getpeername())
            aa = sock.getsockname()
            if sock.getsockname() in picklearray :
                picklearray.remove(sock.getsockname())
            serversdict.extend(picklearray)
            sock.close()
            break
    except ConnectionRefusedError:
        print(f"The server is not active at port {i}")
    except socket.error as e:
        print(f"Error connecting to server on port {i}: {e}")
print("End of searching")
pingallusers()
while True :
    time.sleep(10)
    print("my list : " + str(serversdict))

