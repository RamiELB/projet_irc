import socket
import threading
import sys
import param


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

        # Send UserName Once
        send_message = SendMessage(sc,param.CODES[0] + " " + user_name)
        send_message.start()


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
            print(self.client.socket.recv(param.SIZE).decode(param.FORMAT))



# -------------------------------------------------------------------------------------------#



class WriteServer(threading.Thread):
    def __init__(self, client): 
        threading.Thread.__init__(self) 
        self.client = client

    def code_handler(self, msg):
        code_received = msg.split(' ', 1)[0]


        if code_received == "/help":
            help()

        elif code_received == param.CODES[1]: # JOIN
            code_received = msg.split(' ', 1)
            if len(code_received) == 2:
                client.socket.send(msg.encode(param.FORMAT))
            else:
                print("[ERROR] Must be 1 argument with /join")

        elif code_received == param.CODES[2]: # DISCONNECT
            code_received = msg.split(' ', 1)
            if len(code_received) == 1:
                client.socket.send(msg.encode(param.FORMAT))
            else:
                print("[ERROR] Must be 0 argument with /disconnect")

        elif code_received == param.CODES[3]: # INVITE USER
            code_received = msg.split(' ', 1)
            if len(code_received) == 2:
                client.socket.send(msg.encode(param.FORMAT))
            else:
                print("[ERROR] Must be 1 argument with /invite")
        
        elif code_received == param.CODES[4]: # LIST
            code_received = msg.split(' ', 1)
            if len(code_received) == 1:
                client.socket.send(msg.encode(param.FORMAT))
            else:
                 print("[ERROR] Must be 0 argument with /list")

        elif code_received == param.CODES[5]: #MSG
            code_received = msg.split(' ', 2)
            if len(code_received) >= 2:
                 client.socket.send(msg.encode(param.FORMAT))
            else:
                print("[ERROR] [Canal|UserName] or/and Message Missing")

        elif code_received == param.CODES[6]: #NAMES
            code_received = msg.split(' ', 1)
            if len(code_received) <= 2:
                client.socket.send(msg.encode(param.FORMAT))
            else:
                print("[ERROR] Must be at most 1 argument")                
        else:
            client.socket.send(msg.encode(param.FORMAT))
    
    def run(self):
        while True:
            msg = input('')
            self.code_handler(msg)
           


# -------------------------------------------------------------------------------------------#  


class SendMessage(threading.Thread):
    def __init__(self, server, msg): 
        threading.Thread.__init__(self) 
        self.server = server
        self.msg = msg

    def run(self):
            self.server.send(self.msg.encode(param.FORMAT)) 

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
        client = irc_client(args[0], param.SERVER, int(args[1]))
    else:
        print("[ERROR] 1st argument must be username, 2nd argument must be serve's name")
        