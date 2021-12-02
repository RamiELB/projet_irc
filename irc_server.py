import socket
import threading

class irc_server:
    def __init__(self, server_name):
        self.server_name = server_name
        self.channels = {}
        self.users = {}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', 5777))
        s.listen(10)
        self.main_socket = s

    def new_user(self, user_name):
        new_user = user(user_name)
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

class user:
    def __init__(self, user_name):
        self.user_name = user_name
        self.is_away = False
        self.away_msg = ''

    def away(self, away_msg=''):
        self.is_away = not self.is_away
        self.away_msg = away_msg

    def get_away_msg(self):
        if self.is_away:
            return self.away_msg

serv = irc_server()

thib = serv.new_user("thibo")
thib.away("jme casse les bolosse")
thib.get_away_msg()

serv.connect_to_channel("le binks", "thibo")

print(serv.channels)
print(serv.users)