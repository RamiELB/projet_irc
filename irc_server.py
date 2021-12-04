import socket
import threading
import sys
from irc_client import irc_client


SIZE = 1024
FORMAT = "utf8"
DISCONNECT_MSG = "!DISCONNECT"
NB_CONNECTION = 10
SERVER = 'localhost'


# -------------------------------------------------------------------------------------------#


class channel:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.users = []

    def connect(self, user_name):
        self.users.append(user_name)

    def disconnect(self, user_name):
        if user_name in self.users:
            self.users.remove(user_name)

    def list_users(self):
        return self.users


# -------------------------------------------------------------------------------------------#


class irc_server:
    def __init__(self, server_name, IP, PORT):
        print('[STARTING] Server is starting...')

        # IRC
        self.server_name = server_name
        self.channels = {}
        self.users = {}


        # Main channel
        main_channel = channel("Main")
        self.channels["Main"] = main_channel


        # SERVER
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP, PORT))
        s.listen(NB_CONNECTION)
        self.main_socket = s

        print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    def new_user(self, user_name): 
        new_user = irc_client(user_name)
        self.users[user_name] = new_user
        return new_user

    def connect_to_channel(self, channel_name, user_name):
        if channel_name in self.channels:
            self.channels[channel_name].connect(user_name)
        else:
            c = channel(channel_name)
            self.channels[channel_name] = c
            c.connect(user_name)

    def disconnect_from_channel(self, channel_name, user_name):
        if channel_name in self.channels:
            self.channels[channel_name].disconnect(user_name)
    
    def start(self):
        while True:
            client, addr = self.main_socket.accept()
            handle = ListenClient(client, addr)  
            handle.start()
            self.new_user()
            print(f"[ACTIVE CONNECTION] {threading.active_count() - 1}")


# -------------------------------------------------------------------------------------------#


class ListenClient(threading.Thread):
    def __init__(self,client, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        threading.Thread.__init__(self)
        self.client = client
        self.addr = addr

    def run(self):
        connected = True
        while connected:
            msg = self.client.recv(SIZE).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                connected = False

            print(f"[{self.addr}] {msg}") 

            
            # TODO : PARSE


            msg = f"Msg received: {msg}"
            sendThread = SendMessage(self.client, msg) ## SOIT ON CREE UN THREAD A CHAQUE ENVOIE DE MESSAGE SOIT ON UTILISE LE MEME THREAD QUE CELUI DE LIRE , THREAD EN CONTINUE PAS POSSIBLE ?
            sendThread.start()

       
        self.client.close()


# -------------------------------------------------------------------------------------------#


class SendMessage(threading.Thread):
    def __init__(self, client, msg): 
        threading.Thread.__init__(self) 
        self.client = client
        self.msg = msg
    
    def run(self):
            self.client.send(self.msg.encode(FORMAT))


# -------------------------------------------------------------------------------------------#


if __name__ == "__main__":

    args = sys.argv[1:]
    if len(args) >= 1:
        serv = irc_server(args[0], SERVER,int(args[0]))
        serv.start()
    else:
        print("[ERROR] Missing server's name")