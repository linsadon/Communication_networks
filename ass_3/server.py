import socket
import threading
import pickle
import json
import time
import struct

#('192.168.241.1', 3000)
serversdict=[]
#{'yuval':(socket of '192.168.241.1', 1234)}
clientsdict={}


def heandlclient(sock,v1,v2,v3,v4):
    while True:
        if v1 == 2:
            addclient(sock, v3)
        elif v1 == 3:
            forwardmsg(sock, v3, v4)
        data = sock.recv(6)
        if len(data) == 0:
            sock.close()
            return
        v1, v2, v3, v4 = struct.unpack('>bbhh', data)



def forwardmsg(sock,msgsize,subsize):
    global clientsdict
    data = sock.recv(msgsize).decode()
    print(data)
    sendername = [i for i in clientsdict if clientsdict[i]==sock]
    recipient = data.split()[0]
    if recipient in clientsdict:
        clientsdict[recipient].send(('message from '+ str(sendername[0])+' : ' + data.split(' ', 1)[1]).encode())



def addclient(sock,size):
    global clientsdict
    name = sock.recv(size).decode()
    if name not in clientsdict:
        clientsdict[name] = sock


def addservers(sock,size):
    global serversdict
    data = sock.recv(size)
    picklearray = pickle.loads(data)
    if sock.getpeername() not in serversdict:
        serversdict.append(sock.getpeername())
    if sock.getsockname() in picklearray:
        picklearray.remove(sock.getsockname())
    serversdict.extend(picklearray)
    sock.close()


def createheader(t,st,l,sl):
    return struct.pack('>bbhh',t,st,l,sl)


def pingallusers():
    # socket_objects = []
    global serversdict
    for address in serversdict:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((my_ip, my_port))
        sock.connect(address)
        # socket_objects.append(sock)
        sock.close()
    # for sock in socket_objects:
    #     sock.send("conn try".encode())
    # for sock in socket_objects:
    #     sock.close()


def senddict(conn):
    global serversdict
    picklearray = pickle.dumps(serversdict)
    conn.send(createheader(1, 0, len(picklearray), 0))
    conn.sendall(picklearray)


def acceptconnection(sock):
    while True:
        conn, client_address = sock.accept()
        print('new connection from', client_address)
        # conn.close()
        # print("my list : " + str(serversdict))
        threading.Thread(target=respond_to_connect, args=(conn, client_address)).start()
        #respond_to_connect(conn, client_address)


def respond_to_connect(conn_socket, client_address):
    # while True:
    # 0-----1-----2----------4----------6
    # |type | sub |    len   |   sub    |
    # |     |type |          |   len    |
    global serversdict
    data = conn_socket.recv(6)
    if len(data)==0:
        conn_socket.close()
        return
    v1,v2,v3,v4 = struct.unpack('>bbhh',data)
    print("v1 : ",v1," v2 : ",v2," v3 : ",v3," v4 : ",v4)
    if v1 == 0:
        if client_address not in serversdict:
            serversdict.append(client_address)
        senddict(conn_socket)
    elif v1 == 1:
        if client_address not in serversdict:
            serversdict.append(client_address)
        addservers(conn_socket, v3)
    elif v1 == 2 or v1 == 3:
        threading.Thread(target=heandlclient, args=(conn_socket,v1,v2,v3,v4)).start()
        return
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
            #0-----1-----2----------4----------6
            #|type | sub |    len   |   sub    |
            #|     |type |          |   len    |
            sock.send(createheader(0,0,0,0))
            data = sock.recv(6)
            v1,v2,v3,v4 = struct.unpack('>bbhh',data)
            if v1 == 1:
                addservers(sock,v3)
            elif v1 == 0:
                senddict(sock)
            break
    except ConnectionRefusedError:
        print(f"The server is not active at port {i}")
    except socket.error as e:
        print(f"Error connecting to server on port {i}: {e}")
print("End of searching")
pingallusers()
while True:
    time.sleep(10)
    print("my list : " + str(serversdict))
    print("my client : " + str(clientsdict))

