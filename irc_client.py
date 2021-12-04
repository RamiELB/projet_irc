import socket
import threading
import sys

SIZE = 1024
FORMAT = "utf8"
DISCONNECT_MSG = "!DISCONNECT"
NB_CONNECTION = 10
SERVER = 'localhost'

# -------------------------------------------------------------------------------------------#


class irc_client:
    def __init__(self, user_name, host, port):

        # Main attributes
        self.user_name = user_name
        self.is_away = False
        self.msg_away = '' 

        # Socket
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sc.connect((host,port))
        self.socket = sc

        # Current channel
        self.current_channel = "TBD (lorsqu'on se connecte le serveur doit envoyer son channel principal)"


        # Listen and Write Threads
        self.listen_thread = ListenServer(self)
        self.write_thread = WriteServer(self)
        self.listen_thread.start()
        self.write_thread.start()

    def away(self, away_msg=''):
        self.is_away = not self.is_away
        if away_msg:
            self.away_msg = away_msg

    def get_away_msg(self):
        if self.is_away:
            return self.away_msg

    def change_channel(self, new_channel):
        self.current_channel = new_channel


# -------------------------------------------------------------------------------------------#


class ListenServer(threading.Thread):
    def __init__(self,client): 
        threading.Thread.__init__(self)
        self.client = client
      
    def run(self):
        while True:
            print(self.client.socket.recv(SIZE).decode(FORMAT))



# -------------------------------------------------------------------------------------------#



class WriteServer(threading.Thread):
    def __init__(self, client): 
        threading.Thread.__init__(self) 
        self.client = client
    
    def run(self):
        while True:
            msg = input('')

            parse = msg.split(' ', 1)
            if parse[0] == '/help':
                help()
            else:
                self.client.socket.send(msg.encode('utf8'))


# -------------------------------------------------------------------------------------------#   


def help():
        print('/away [message]')
        print('/help')
        print('/invite <user_name>')
        print('/join <channel> [ckey]')
        print('/list')
        print('/msg [canal|nick] message')
        print('/names [channel]')



# -------------------------------------------------------------------------------------------#


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        client = irc_client(args[0],SERVER,int(args[1]))
    else:
        print("[ERROR] 1st argument must be username, 2nd argument must be serve's name")
        