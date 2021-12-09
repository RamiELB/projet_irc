import socket
import threading
import sys
import param

# -------------------------------------------------------------------------------------------#


class irc_server:
    def __init__(self, server_name, IP, PORT):
        print('[STARTING] Server is starting...')

        # IRC
        self.server_name = server_name
        self.canals = {}
        self.users = {}
        self.nb_users = 0


        # Main canal
        main_canal = Canal("#Main")
        self.canals["#Main"] = main_canal


        # SERVER
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP, PORT))
        s.listen(param.NB_CONNECTION)
        self.main_socket = s

        print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    def new_user(self, user_name, client): 
        self.users[user_name] = client
        client.create_user(user_name)
        self.connect_to_canal("#Main", client)
        self.nb_users += 1
        
    def list_canals(self):
        return list(self.canals.keys())

    def connect_to_canal(self, canal_name, client):
        if canal_name in self.canals:
            self.canals[canal_name].connect(client)
        else:
            c = Canal(canal_name)
            self.canals[canal_name] = c
            c.connect(client)
        msg = "[CONNECTED] " + canal_name
        sendThread = SendMessageToUser(None, client, msg)
        sendThread.start()

    def disconnect_from_canal(self, canal_name, client):
        if canal_name in self.canals:
            self.canals[canal_name].disconnect(client)
    
    def start(self):
        while True:
            socket_client, addr = self.main_socket.accept()
            handle = HandleClient(self, socket_client, addr)  
            handle.start()
            print(f"[ACTIVE CONNECTION] {threading.active_count() - 1}")

    def list_users(self):
        return list(self.users.keys())

    def get_user_by_username(self, user_name):
        if user_name in self.list_users():
            return self.users[user_name]
        return None

    def get_canal_by_name(self, name):
        if name in self.list_canals():
            return self.canals[name]
        return None
# -------------------------------------------------------------------------------------------#


class Canal:
    def __init__(self, canal_name):
        self.canal_name = canal_name
        self.users = {}

    def connect(self, client):
        self.users[client.user_name] = client
        client.change_canal(self)

    def disconnect_from_canal(self, client):
        self.users.pop(client.user_name, None)

    def list_users(self):
        return self.users

    def get_canal_name(self):
        return self.canal_name

# -------------------------------------------------------------------------------------------#

class Client:
    def __init__(self, socket_client):
        self.socket_client = socket_client
        self.current_canal = None
        
    def create_user(self, user_name):
        self.user_name = user_name
        self.is_away = False
        self.msg_away = ''

    def away(self, away_msg=''):
        self.is_away = not self.is_away
        if away_msg:
            self.away_msg = away_msg

    def get_away_msg(self):
        if self.is_away:
            return self.away_msg

    def change_canal(self, new_canal):
        if self.current_canal != None:
            self.current_canal.disconnect_from_canal(self)
        self.current_canal = new_canal

    def recv_msg(self):
        return self.socket_client.recv(param.SIZE).decode(param.FORMAT)

    def send_msg(self, msg):
        self.socket_client.send(msg.encode("utf-8"))

    def disconnect(self):
        self.current_canal.disconnect_from_canal(self)
        self.socket_client.close()

    def get_canal(self):
        return self.current_canal

    def get_user_name(self):
        return self.user_name

# -------------------------------------------------------------------------------------------#


class HandleClient(threading.Thread):
    def __init__(self, server, socket_client, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        threading.Thread.__init__(self)
        self.server = server
        self.client = Client(socket_client)
        self.addr = addr

    def codes_handler(self, code_received, msg):
        if code_received == param.CODES[0]: 
            #USERNAME
            user_name = msg.split(' ', 2)[1]
            self.server.new_user(user_name, self.client)
        
        elif code_received == param.CODES[1]:
            #JOIN
            new_canal_name = msg.split(' ', 2)[1]
            self.server.connect_to_canal(new_canal_name, self.client)

        elif code_received == param.CODES[2]:
            #DISCONNECT
            self.client.disconnect()
            self.connected = False

        elif code_received == param.CODES[3]:
            #INVITE
            user_name = msg.split(' ', 2)[1]
            invited_user = self.server.get_user_by_username(user_name)
            if invited_user == None:
                sendThread = SendMessageToUser(None, self.client, "[ERROR] user " + user_name + " does not exist.")
                sendThread.start()
            else:
                sendThread = SendMessageToUser(None, invited_user, "[INVITE] " + self.client.user_name + " " + self.client.get_canal().get_canal_name())
                sendThread.start()

        elif code_received == param.CODES[4]:
            #LIST
            msg = "List of available canals:"
            for canal_name in self.server.list_canals():
                msg = msg + " " + canal_name
            sendThread = SendMessageToUser(None, self.client, msg)
            sendThread.start()

        elif code_received == param.CODES[5]:
            #MSG
            name = msg.split(' ', 2)[1]
            if name[0] == "#":
                #msg to canal
                canal = self.server.get_canal_by_name(name)
                if canal == None :
                    sendThread = SendMessageToUser(None, self.client, "[ERROR] canal " + name + " does not exist.")
                else:
                    sendThread = SendMessage(self.client, msg, canal)
                sendThread.start()
            else:
                target_user = self.server.get_user_by_username(name)
                if target_user == None:
                    sendThread = SendMessageToUser(None, self.client, "[ERROR] user " + name + " does not exist.")
                else:
                    sendThread = SendMessageToUser(self.client, target_user, msg.split(' ', 2)[2])
                sendThread.start()

        elif code_received == param.CODES[6]:
            #NAMES
            pass




    def run(self):
        self.connected = True

        while self.connected:
            msg = self.client.recv_msg()
            parse_msg = msg.split(' ', 1)
            
            code_received = parse_msg[0]

            if code_received in param.CODES:
                self.codes_handler(code_received, msg)
            else :
                sendThread = SendMessage(self.client, msg)
                sendThread.start()
        


# -------------------------------------------------------------------------------------------#


class SendMessage(threading.Thread):
    #send a message to a canal
    def __init__(self, client, msg, canal=None): 
        threading.Thread.__init__(self) 
        self.client = client

        if canal == None:
            self.canal = self.client.current_canal
        else:
            self.canal = canal

        self.msg = client.user_name + ': ' + msg
    
    def run(self):
        for c in self.canal.users.values():
            c.send_msg(self.msg)

class SendMessageToUser(threading.Thread):
    #send a message to a user
    def __init__(self, client_from, client_to, msg): 
        threading.Thread.__init__(self)
        self.client_to = client_to 
        self.msg = msg

        if client_from != None:
            # else = message from server
            self.msg = "("+client_from.get_user_name()+") " + self.msg
    
    def run(self):
        print("ENVOIE DU MSG "+ self.msg + " A " + self.client_to.get_user_name())
        self.client_to.send_msg(self.msg)


# -------------------------------------------------------------------------------------------#


if __name__ == "__main__":

    args = sys.argv[1:]
    if len(args) >= 1:
        serv = irc_server(args[0], param.SERVER, int(args[0]))
        serv.start()
    else:
        print("[ERROR] Missing server's name")