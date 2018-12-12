import socket
import threading
import queue
import time

host = "127.0.0.1"
port = 9000
buffer_size = 1024
host_and_port = (host, port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(host_and_port)
server_socket.listen(10)


class Server:
    def __init__(self):
        #
        # Vi laver en tom liste, som skal indeholde alle vores clients
        self.clients = []

        # Vi laver en queue, som skal indeholde alle beskederne
        self.messages = queue.Queue()

        threading.Thread(target=self.broadcast_messages).start()

        self.accept_connections()

        self.handle_client(server_socket)

    def accept_connections(self):
        # Vi sætter antallet af nicknames til 0,
        # så hver gang en klient bliver tilføjet bliver denne variabel inkrementeret med 1
        nicknames = 0
        while True:
            conn, addr = server_socket.accept()
            client_dict = {"NICKNAME": nicknames, "HEARTBEAT": time.time(), "CLIENT": conn}
            self.clients.append(client_dict)
            nicknames += 1
            print("New client joined the chat", addr)
            t = threading.Thread(target=self.client_thread, args=(conn,))
            t.start()

    def broadcast_messages(self):
        while True:
            msg = self.messages.get()
            for c in self.clients:
                c["CLIENT"].send(msg.encode())

    def client_thread(self, conn):
        while True:
            msg = conn.recv(1024).decode()
            self.messages.put(msg)
            print("Message from client: ", msg)

    # Tager en klient socket som parameter
    def handle_client(self, client):
        """Handles a single client connection."""

        name = client.recv(buffer_size).decode()
        welcome = 'Welcome %s! Type quit to exit the chat.' % name
        client.send(bytes(welcome, "utf8"))
        msg = "%s has joined the chat!" % name
        self.broadcast_messages(bytes(msg, "utf8"))
        self.clients[client] = name

        while True:
            msg = client.recv(buffer_size)
            if msg != bytes("quit", "utf8"):
                self.broadcast_messages(msg, name+": ")
            else:
                client.send(bytes("quit", "utf8"))
                client.close()
                del self.clients[client]
                self.broadcast_messages(bytes("%s has left the chat." % name, "utf8"))
                break


server = Server()




