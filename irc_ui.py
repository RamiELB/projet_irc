import tkinter as tk
import threading
import param




class irc_ui(tk.Frame):
	def __init__(self, client):
	
		# client
		self.client = client


		#tkinter Object
		self.root = tk.Tk()
		self.root.geometry("900x500")
		
	
		self.Output = tk.Text(self.root, height = 15,
			width = 100,
			bg = "light cyan")
		self.Output.bind("<Key>", lambda e: "break")


		self.Input = tk.Text(self.root, height = 5,
				width = 100,
				bg = "light yellow")
		self.root.bind('<Return>', self.callback)
        
		# Threads
		self.listen_thread = ListenServer(self.client, self)
		self.listen_thread.start()

	# update the title with the name and the current canal
	def update_title(self):
		self.root.title(self.client.user_name + " : " + self.client.current_canal)

	# Enter Event
	def callback(self, event):
		self.take_input(event)

	# Take the input of the user
	def take_input(self, event):
		INPUT = self.Input.get("1.0", "end-2c")
		if self.code_handler(INPUT):
			send_message = SendMessage(self.client.socket, INPUT)
			send_message.start()
			if INPUT == param.CODES[2]:
				self.root.quit()

		self.Input.delete("1.0", tk.END)

	def start(self):
		# Pack
		self.Output.pack()
		self.Input.pack()

		# start
		self.root.mainloop()

	def code_handler(self, msg):
		code_received = msg.split(' ', 1)[0]
		toSend = False
		error = ""


		if self.client.invitation[0]:
			if code_received == "oui":
				msg = param.CODES[1] + " " + self.client.invitation[1]
				send_message = SendMessage(self.client.socket, msg)
				send_message.start()
			else:
				self.client.invitation = [False,""]

		elif code_received == "/help":
			toPrint = '/away [message] \n'\
			+ ('/help  \n')\
        	+ ('/invite <user_name>\n')\
        	+ ('/join <canal> [ckey]\n')\
        	+ ('/list\n')\
        	+ ('/msg [canal|nick] message\n')\
        	+ ('/names [canal]')
			self.Output.insert(tk.END, toPrint + "\n")

		elif code_received == param.CODES[1]: # JOIN
			code_received = msg.split(' ', 1)
			if len(code_received) == 2:
				if (code_received[1][0] == "#"):
					toSend = True
				else:
					error = ("[ERROR] Canal name must start with #")
			else:
				error = ("[ERROR] Must be 1 argument with /join")

		elif code_received == param.CODES[2]: # DISCONNECT
			code_received = msg.split(' ', 1)
			if len(code_received) == 1:
				toSend = True
			else:
				error = ("[ERROR] Must be 0 argument with /disconnect")

		elif code_received == param.CODES[3]: # INVITE USER
			code_received = msg.split(' ', 1)
			if len(code_received) == 2:
				toSend = True
			else:
				error = ("[ERROR] Must be 1 argument with /invite")

		elif code_received == param.CODES[4]: # LIST
			code_received = msg.split(' ', 1)
			if len(code_received) == 1:
				toSend = True
			else:
					error = ("[ERROR] Must be 0 argument with /list")

		elif code_received == param.CODES[5]: #MSG
			code_received = msg.split(' ', 2)
			if len(code_received) >= 2:
					toSend = True
			else:
				error = ("[ERROR] [Canal|UserName] or/and Message Missing")

		elif code_received == param.CODES[6]: #NAMES
			code_received = msg.split(' ', 1)

			if len(code_received) == 2:
				if (code_received[1][0] == "#"):
					toSend = True
				else:
					error = ("[ERROR] Canal Name must start with #")

			elif len(code_received) == 1:
				toSend = True
			else:
				error = ("[ERROR] Must be at most 1 argument")                
		else:
			toSend = True

		if not toSend:
				self.Output.insert(tk.END, error + "\n")

		return toSend

class ListenServer(threading.Thread):
	def __init__(self,client, ui): 
		threading.Thread.__init__(self)
		self.client = client
		self.ui = ui
		
	def code_handler(self, msg):
		code_received = msg.split(' ', 1)[0]
		if code_received == "[CONNECTED]":
			canal = msg.split(' ', 1)[1]
			self.client.current_canal = canal
			self.ui.update_title()
			msg = "Vous avez rejoint le canal " + canal

			if self.client.invitation[0]: 
				self.client.invitation = [False,""]
			
		elif code_received == "[INVITE]":
			split = msg.split(' ', 2)
			user = split[1]
			canal_name = split[2]
			self.client.invitation = [True, canal_name]
			msg = user + " vous invite dans le canal " + canal_name + " (oui/non)"


		return msg

	def run(self):
		while True:
			msg = self.client.socket.recv(param.SIZE).decode(param.FORMAT)
			toPrint = self.code_handler(msg)
			self.ui.Output.insert(tk.END, toPrint + "\n")

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
        print('/join <canal> [ckey]')
        print('/list')
        print('/msg [canal|nick] message')
        print('/names [canal]')