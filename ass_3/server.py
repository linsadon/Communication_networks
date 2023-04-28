import socket
import threading
import pickle
import json
import time
import struct

#(socket of '192.168.241.1', 3000)
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
        v1, v2, v3, v4 = struct.unpack('>bbhh', data)


def forwardmsg(sock,msgsize,subsize):
    stopsearching = 0
    global clientsdict
    global serversdict
    data = sock.recv(msgsize).decode()
    if '\0' in data[:subsize]:
        split_users = data[:subsize].split('\0')
        sendername = split_users[0]
        recipient = split_users[1]
        stopsearching = 1
    else:
        sendername = [i for i in clientsdict if clientsdict[i]==sock][0]
        recipient = data[:subsize]
    if recipient in clientsdict:
        clientsdict[recipient].send(('message from ' + str(sendername)+' : ' + data[subsize+1:]).encode())
        return
    if not stopsearching:
        for i in serversdict:
            participants = str(sendername) + '\0' + str(recipient)
            i.send(createheader(3,0,len(participants+" "+data[subsize+1:]),len(participants)))
            i.send((participants+" "+data[subsize+1:]).encode())


def addclient(sock,size):
    global clientsdict
    name = sock.recv(size).decode()
    if name not in clientsdict:
        clientsdict[name] = sock


def addservers(sock,size):
    global serversdict
    data = sock.recv(size)
    picklearray = pickle.loads(data)
    if sock not in serversdict:
        serversdict.append(sock)
    if sock.getsockname() in picklearray:
        picklearray.remove(sock.getsockname())

    templist= convert_addr_to_sock(picklearray)
    serversdict.extend(templist)
    #sock.close()


def createheader(t,st,l,sl):
    return struct.pack('>bbhh',t,st,l,sl)


def convert_addr_to_sock(list):
    socket_objects = []
    for address in list:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((my_ip, my_port))
        sock.connect(address)
        socket_objects.append(sock)
        #sock.close()
    return socket_objects


def pingallusers(list):
    for address in list:
        address.send(createheader(4,0,0,0))


def senddict(conn):
    global serversdict
    sending_server_list=[i.getpeername() for i in serversdict]
    picklearray = pickle.dumps(sending_server_list)
    conn.send(createheader(1, 0, len(picklearray), 0))
    conn.sendall(picklearray)


def acceptconnection(sock):
    while True:
        conn, client_address = sock.accept()
        print('new connection from', client_address)
        threading.Thread(target=respond_to_connect, args=(conn, client_address)).start()


def respond_to_connect(conn_socket, client_address):
    # 0-----1-----2----------4----------6
    # |type | sub |    len   |   sub    |
    # |     |type |          |   len    |
    global serversdict
    global endsending
    while True:
        data = conn_socket.recv(6)
        v1,v2,v3,v4 = struct.unpack('>bbhh',data)
        if v1 == 0:
            if conn_socket not in serversdict:
                serversdict.append(conn_socket)
            senddict(conn_socket)
        elif v1 == 1:
            if conn_socket not in serversdict:
                serversdict.append(conn_socket)
            addservers(conn_socket, v3)
            pingallusers(serversdict)
        elif v1 == 2 or v1 == 3:
            threading.Thread(target=heandlclient, args=(conn_socket,v1,v2,v3,v4)).start()
            break
        elif v1 == 4:
            if conn_socket.getpeername() not in [i.getpeername() for i in serversdict]:
                serversdict.append(conn_socket)
    #conn_socket.close()


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
            threading.Thread(target=respond_to_connect, args=(sock, '0.0.0.0')).start()
            break
    except ConnectionRefusedError:
        print(f"The server is not active at port {i}")
    except socket.error as e:
        print(f"Error connecting to server on port {i}: {e}")
print("End of searching")
while True:
    time.sleep(10)
    print("my addr : " , [i.getpeername() for i in serversdict ])
    print("my client : " + str(clientsdict))

