import socket
from tkinter import *
from tkinter import messagebox
import threading


class Client:

    def __init__(self, root):
        # Sætter forbindelsen op
        self.host = "127.0.0.1"
        self.port = 9000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        # GUI'en starter her
        self.root = root
        self.root.title("Your nickname")

        self.nickname_frame = Frame(self.root)
        self.nickname_frame.grid(column=0, row=0)

        self.nickname_string = ""
        self.nickname_string_var = StringVar()
        self.nickname_string_var.set("")

        enter_nickname = Label(self.nickname_frame, text="Enter your desired nickname:")
        enter_nickname.grid(column=0, row=0)

        nickname_entry = Entry(self.nickname_frame, textvariable=self.nickname_string_var)

        nickname_entry.grid(column=0, row=1)

        # Før brugte vi pack
        # nickname_entry.pack(fill=X)

        # Når brugeren trykker på send-knappen, bliver kommandoen loginGui refereret
        send_button = Button(self.nickname_frame, text="Submit nickname", command=self.login_gui,
                             bg="green", fg="black", padx=2)
        send_button.grid(column=1, row=1)

        self.login_frame = Frame(self.root)

        self.username = StringVar()
        self.username.set("")
        self.password = StringVar()
        self.password.set("")

    def toggle_chat(self):
        self.nickname_string = self.nickname_string_var.get()
        self.root.title("Mathias' chat")
        self.nickname_frame.grid_remove()
        self.root.geometry("400x400")
        messages_frame = Frame(self.root)
        scrollbar = Scrollbar(messages_frame)

        # Har gjort denne variabel global, fordi den skal kunne tilgås over alt.
        # Det er for, at __init__-metoden ikke bliver for stor.
        global msg_list
        msg_list = Listbox(messages_frame, bg="lightblue", height=30, width=60, yscrollcommand=scrollbar.set)

        # To see through previous messages.
        scrollbar.pack(side=RIGHT, fill=Y)
        msg_list.pack(side=LEFT, fill=BOTH)
        msg_list.pack()

        messages_frame.pack()
        global my_msg
        my_msg = StringVar()

        entry_field = Entry(self.root, textvariable=my_msg)

        my_msg.set(entry_field.get())

        entry_field.bind("<Return>", func=lambda f: self.send_message())
        entry_field.pack(fill=X)

        send_msg_button = Button(self.root, text="Send message", command=self.send_message, bg="green", fg="black")
        send_msg_button.pack()
        change_nickname_field = Entry(self.root, textvariable=self.nickname_string_var)
        change_nickname_field.pack(fill=X)

        change_nickname_btn = Button(self.root, text="Change your Nickname",
                                     command=lambda: self.change_nickname(self.nickname_string_var),
                                     bg="green", fg="black")
        change_nickname_btn.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.start()

    def login(self):
        login_file = open("user_details.txt", "r")
        content = login_file.readlines()
        content = [x.strip() for x in content]
        print("Username: " + content[0])
        print("Password: " + content[1])

        if self.username.get() == content[0] and self.password.get() == content[1]:
            self.login_frame.grid_remove()
            self.toggle_chat()
        else:
            wrong_password_label = Label(self.login_frame, text="You entered a wrong password", fg="red")
            wrong_password_label.grid(row=2, column=2)

    def login_gui(self):
        # man skal ikke blive navigeret hertil, hvis man ikke angiver et nickname
        if self.nickname_string_var.get() != "":
            self.root.geometry("400x400")
            self.root.title("Login with your credentials")
            self.nickname_frame.grid_remove()
            self.login_frame.grid()
        else:
            messagebox.showwarning("Warning", "You must specify a nickname")
        username_label = Label(self.login_frame, text="Username")
        username_label.grid(row=0, column=0)

        password_label = Label(self.login_frame, text="Password")
        password_label.grid(row=1, column=0)

        username_entry = Entry(self.login_frame, textvariable=self.username)
        username_entry.grid(row=0, column=1)

        password_entry = Entry(self.login_frame, textvariable=self.password)
        password_entry.grid(row=1, column=1)

        explanatory_message = Label(self.login_frame, text="Click login to submit", fg="green")
        explanatory_message.grid(row=2, column=1)

        submit_button = Button(self.login_frame, text="Login", command=self.login, bg="green", fg="black")
        submit_button.grid(row=2, column=2)

    def change_nickname(self, nickname):
        self.nickname_string = nickname.get()
        messagebox.showinfo("Just changed your nickname", "You have changed your nickname to: " + nickname.get())

    def on_closing(self):
        """This function is to be called when the window is closed."""
        my_msg.set("quit")
        self.send_message()

    def send_message(self):
        global my_msg
        msg = my_msg.get()
        message_to_be_sent = self.nickname_string + ": " + msg
        self.sock.send(message_to_be_sent.encode())
        if msg == "quit":
            self.sock.close()
            self.root.quit()

    @staticmethod
    def receive_message(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                print(msg)
                msg_list.insert(END, msg)
                msg_list.see(END)
            except OSError:
                break


# Laver startvinduet, som starter applikationen
start_window = Tk()
start_window.geometry("400x400")

# Instantierer klient-klassen
client = Client(start_window)
start_window.mainloop()