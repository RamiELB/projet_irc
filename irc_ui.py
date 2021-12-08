from tkinter import *

root = Tk()
root.geometry("1000x800")
root.title(" Q&A ")

Output = Text(root, height = 5,
			width = 25,
			bg = "light cyan")


				
l = Label(text = "IRC_SERVER")
inputtxt = Text(root, height = 10,
				width = 25,
				bg = "light yellow")



def Take_input():
	INPUT = inputtxt.get("1.0", "end-1c")
	print(INPUT)
	Output.insert(END, INPUT + "\n")
	inputtxt.delete("1.0", "end-1c")
	


l.pack()
inputtxt.pack()
Output.pack()

mainloop()
