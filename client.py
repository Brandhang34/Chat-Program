import socket
import pickle
import threading
from tkinter import *

def connect(name, host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send(name.encode('utf-8'))
    return client


def send_message(client, msg):
    message = msg.encode('utf-8')
    client.send(message)


def receive_message(client):
    try: 
        receiving = True
        while receiving:
            message = client.recv(1024)
            try:
                message = message.decode('utf-8')
            except UnicodeDecodeError:
                message = pickle.loads(message)

            # Checks if the message is a list and inserts into the Users text box
            if type(message) == list and message:
                ActiveUser_text.config(state=NORMAL)
                ActiveUser_text.delete("1.0","end")
                for user in message:
                    ActiveUser_text.insert(INSERT, f'{user}\n')
                ActiveUser_text.config(state=DISABLED)

            # Checks for anything other than !Exit
            if type(message) != str:
                pass
            elif message != "!Exit":
                Chat_text.config(state=NORMAL)
                Chat_text.insert(INSERT, f'{message}\n')
                Chat_text.config(state=DISABLED)
            else:
                receiving = False

    except RuntimeError:
        print("Exiting Thread")


def Send_button_clicked_Chat():
    message = Chat_input.get()
    Chat_text.config(state=NORMAL)
    send_message(client, message)
    Chat_text.configure(state='disabled')
    Chat_input.delete(0, 'end')


def Send_button_clicked_Username():
    username.set(Username_entry.get())
    Host.set(Host_entry.get())
    Port.set(Port_entry.get())
    UsernameInput_window.destroy()


def Disconnect_button_clicked_Chat():
    ChatProgram_window.destroy()
    send_message(client, "!Exit")
    print("*** Disconnected ***")
    raise SystemExit


def Disconnect_button_clicked_Username():
    UsernameInput_window.destroy()
    raise SystemExit

'''
**********************************************************************
*********************************MAIN*********************************
**********************************************************************
'''

'''
********************************* Username Input *********************************
'''
try:
    UsernameInput_window = Tk()
    UsernameInput_window.eval('tk::PlaceWindow . center')
    UsernameInput_window.title("Enter Username")
    UsernameInput_window.config(padx=30, pady=10)

    Username_label = Label(text="Username: ", font=("Arial", 14, "bold"))
    Username_label.grid(column=1, row=0, pady=(30,5), sticky="W")

    Colon_label = Label(text=":", font=("Arial", 14, "bold"))
    Colon_label.grid(column=2, row=3, sticky="W", padx=(15))

    Host_label = Label(text="Host IP & Port: ", font=("Arial", 14, "bold"))
    Host_label.grid(column=1, row=2, pady=(30,5),columnspan=2, sticky="W")

    username = StringVar()
    Host = StringVar()
    Port = StringVar()

    Username_entry = Entry(width = 30)
    Username_entry.grid(column=1, row=1, columnspan=2, ipady=5, sticky="W")
    Username_entry.focus()

    Host_entry = Entry(width = 20)
    Host_entry.grid(column=1, row=3, columnspan=2, ipady=5, sticky="W")
    Host_entry.insert(0,"localhost")

    Port_entry = Entry(width = 5)
    Port_entry.grid(column=2, row=3, columnspan=1, ipady=5, sticky="E")
    Port_entry.insert(0,"9898")

    Send_button = Button(text="Connect", command=lambda: Send_button_clicked_Username(), width=8)
    UsernameInput_window.bind('<Return>', lambda event: Send_button_clicked_Username())
    Send_button.grid(column=1, row=4, columnspan=2, pady=25)   

    UsernameInput_window.protocol("WM_DELETE_WINDOW", Disconnect_button_clicked_Username)

    UsernameInput_window.mainloop()

except KeyboardInterrupt:
    print("Keyboard interrupt: Exiting Program")
    Disconnect_button_clicked_Username()
    raise SystemExit
except:
    print("Error in User Window Program")
    raise SystemExit


'''
********************************* Chat Program *********************************
'''

try:
    HOST = Host.get()
    PORT = int(Port.get())

    client = connect(username.get(), HOST, PORT)
    thread = threading.Thread(target=receive_message, args=(client,))
    thread.start()
except ConnectionRefusedError:
    print("ERROR: Server is not running or not accepting connections")
    raise SystemExit


try:
    ChatProgram_window = Tk()
    ChatProgram_window.eval('tk::PlaceWindow . center')
    ChatProgram_window.title("Chatting Program")
    ChatProgram_window.config(padx=40, pady=10)

    # Label

    ChatBox_label = Label(text=f"(My IP: {client.getsockname()[0]} Port: {client.getsockname()[1]})\n\nChat Box", font=("Arial", 18, "bold"),justify=LEFT)
    ChatBox_label.grid(column=1, row=0, pady = 10, sticky="W")

    EnterMessage_label = Label(text="Enter Message", font=("Arial", 18, "bold"))
    EnterMessage_label.grid(column=1, row=3, pady=(30,5), sticky="W")

    ConnectedUsers_label = Label(text="Users", font=("Arial", 12, "bold"))
    ConnectedUsers_label.grid(column=3, row=1, pady=5)

    # Text Box

    Chat_text = Text(ChatProgram_window, font=("Arial", 12, "bold"), width=60)
    Chat_text.grid(column=1, row=1,  columnspan=2, rowspan=2)
    send_message(client, "!ShowUserHasConnected")
    Chat_text.config(state=DISABLED)

    Chat_Scroll=Scrollbar(ChatProgram_window, orient='vertical')
    Chat_Scroll.grid(column=2, row=1, sticky="nse", rowspan=2)
    Chat_Scroll.config(command=Chat_text.yview)
    Chat_text.configure(yscrollcommand=Chat_Scroll.set)

    ActiveUser_text = Text(ChatProgram_window, font=("Arial", 12, "bold"), width=15, height=22)
    ActiveUser_text.grid(column=3, row=2, padx=15,sticky="S")

    send_message(client, "!GetAllActiveUsers") # Get a list of all active users connected to the server
    ActiveUser_text.config(state=DISABLED)

    # Entry

    Chat_input = Entry(width = 83)
    Chat_input.grid(column=1, row=4, columnspan=2, ipady=5, sticky="W")
    Chat_input.focus()

    #Button

    Send_button = Button(text="Send", command=lambda: Send_button_clicked_Chat(), width=15)
    ChatProgram_window.bind('<Return>', lambda event: Send_button_clicked_Chat())
    Send_button.grid(column=3, row=4)

    Disconnect_button = Button(text="Disconnect", command=lambda: Disconnect_button_clicked_Chat(), width = 45)
    Disconnect_button.grid(column=0, row=5, columnspan=5, pady = 50)

    ChatProgram_window.protocol("WM_DELETE_WINDOW", Disconnect_button_clicked_Chat)

    ChatProgram_window.mainloop()
except KeyboardInterrupt:
    print("Keyboard interrupt: Exiting Program")
    Disconnect_button_clicked_Chat()
    raise SystemExit
except:
    print("Error in Chat Window Program")
    raise SystemExit

thread.join()
