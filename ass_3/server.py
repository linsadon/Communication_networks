import socket
import threading
import pickle
import json


serversdict=[]
clientsdict={}

def senddict(conn):
    conn.sendall(pickle.dumps(serversdict))

def acceptconnection(sock):
    while True:
        conn, client_address = sock.accept()
        print('new connection from', client_address)
        senddict(conn)
        global serversdict
        serversdict.append(conn.getpeername())
        threading.Thread(target=respond_to_client, args=(conn, client_address)).start()


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
            data = sock.recv(4096)
            picklearray = pickle.loads(data)
            print(picklearray)
            ###################################################
            #print('received from ', sock.getpeername(), sock.recv(1024).decode())
            serversdict.append(sock.getpeername())
            print(serversdict)
            sock.close()
            break
    except ConnectionRefusedError:
        print(f"The server is not active at port {i}")
    except socket.error as e:
        print(f"Error connecting to server on port {i}: {e}")
print("End of searching")

