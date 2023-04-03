import socket
import threading
import pickle
import json


serversdict=[]
clientsdict={}


def pingallusers():
    socket_objects = []
    global serversdict
    for address in serversdict:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((my_ip, my_port))
        sock.connect(address)
        socket_objects.append(sock)
    # for sock in socket_objects:
    #     sock.send("conn try".encode())
    for sock in socket_objects:
        sock.close()

def senddict(conn):
    conn.sendall(pickle.dumps(serversdict))

def acceptconnection(sock):
    while True:
        conn, client_address = sock.accept()
        print('new connection from', client_address)
        global serversdict
        if client_address not in serversdict:
            senddict(conn)
            serversdict.append(client_address)
        conn.close()
        print("my list : " + str(serversdict))
        #threading.Thread(target=respond_to_client, args=(conn, client_address)).start()


def respond_to_client(conn_socket, client_address):
    # while True:
    conn_socket.send("shalachti milonn ".encode())
    print(serversdict)


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
            data = sock.recv(4096)
            picklearray = pickle.loads(data)
            ###################################################
            #print('received from ', sock.getpeername(), sock.recv(1024).decode())
            serversdict.append(sock.getpeername())
            serversdict.extend(picklearray)
            print("origin : " +str(serversdict))
            sock.close()
            break
    except ConnectionRefusedError:
        print(f"The server is not active at port {i}")
    except socket.error as e:
        print(f"Error connecting to server on port {i}: {e}")
print("End of searching")
pingallusers()

