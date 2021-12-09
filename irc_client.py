import socket
import sys
import param
from irc_ui import irc_ui
from irc_ui import SendMessage


class irc_client:
    def __init__(self, user_name, host, port):

        # Main attributes
        self.user_name = user_name
        self.is_away = False
        self.msg_away = '' 
        self.disconnect = False

        # Socket
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sc.connect((host,port))
        self.socket = sc

        # Current canal
        self.current_canal = None # By default

        # Send UserName Once
        send_message = SendMessage(sc,param.CODES[0] + " " + user_name)
        send_message.start()

        # IRC_UI
        self.ui = irc_ui(self)
        self.ui.start()

    def away(self, away_msg=''):
        self.is_away = not self.is_away
        if away_msg:
            self.away_msg = away_msg

    def get_away_msg(self):
        if self.is_away:
            return self.away_msg

    def change_canal(self, new_canal):
        self.current_canal = new_canal

# -------------------------------------------------------------------------------------------#


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        client = irc_client(args[0], param.SERVER, int(args[1]))
    else:
        print("[ERROR] 1st argument must be username, 2nd argument must be serve's name")
        