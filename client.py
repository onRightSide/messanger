from threading import Thread
from datetime import datetime
from socket import socket
from multiprocessing import Queue
from tkinter import *

from log import client_log_config
from utils import encode_message, decode_message, get_message_template
from configs import ADDRESS, PORT, MESSAGE_SIZE


class Client:

    def __init__(self):
        self.s = socket()
        self.nickname = ""
        self.login = ""
        self.password = ""
        self.message_handler = self.MessageHandler(self.s)
        self.gui = self.GUI(self.nickname)

        self.receive_queue = Queue()
        self.send_queue = Queue()

    # run() connects to server and receives a response from it by running connect(). Then it checks the response
    # number field, and, if the connection is successful, starts sending and receiving loops
    # (Now it also handles messages from receive_queue, while the gui is not ready)

    def run(self) -> None:

        response = self.connect()

        print(response)

        if response["response"] == 200:
            client_log_config.logger.info("Connection successful")

            self.run_loops()

            self.gui.run()

        else:
            print("Here1")
            self.close_connection()
            client_log_config.logger.critical("Connection error")
            exit(-1)

    # send_message_loop() is cycle where message is taken from send_queue and sended to server
    # by send_message method of MessageHandler

    def send_message_loop(self) -> None:
        while True:
            text = self.gui.input_queue.get()

            message = self.message_handler.make_message(self.nickname, text)

            self.message_handler.send_message(message)

    # get_message_loop() is cycle where message is received from server by receive_message method of MessageHandler
    # and put to receive_queue

    def get_message_loop(self) -> None:
        while True:

            message = self.message_handler.receive_message()
            print("recieved")
            self.receive_queue.put(message)
            self.gui.output_queue.put(message)

    # run_threads() starts sending and getting loops

    def run_loops(self) -> None:

            client_log_config.logger.info("Running threads")
            print("Here1")
            send_loop = Thread(target=self.send_message_loop, daemon=True)
            print("Here1")
            get_loop = Thread(target=self.get_message_loop, daemon=True)

            send_loop.start()
            get_loop.start()


    # connect() sends a presence message to server, receiving and returning json response from server

    def connect(self) -> dict:

        self.s.connect((ADDRESS, PORT))
        presence = self.message_handler.make_presence(self.login, self.password)
        self.message_handler.send_message(presence)

        return self.message_handler.receive_message()

    # close_connection() send an exit message to server and closes client connection

    def close_connection(self) -> None:
        exit_ = self.message_handler.make_exit()
        self.message_handler.send_message(exit_)
        self.s.close()

    # MessageHandler class unites all the methods, serves to make standart messages from message template,
    # to send and receive messages

    class MessageHandler:

        def __init__(self, s: socket):
            self.socket = s

        # send_message() simply sends ready message

        def send_message(self, message: dict) -> None:

            self.socket.send(encode_message(message))

        # receive_message() simply receives a message from server, decodes it and returns it

        def receive_message(self) -> dict:
            message = decode_message(self.socket.recv(MESSAGE_SIZE))
            print("Message received")
            return message

        # make_presence() gets a message template dict and makes presence message, recognized by server

        def make_presence(self, login: str, password: str) -> dict:
            message = get_message_template()
            message["action"] = "presence"
            message["time"] = datetime.now().strftime('%H:%M:%S')
            message["login"] = login
            message["password"] = password
            return message

        # make_message() gets a message template dict and makes message the user sees on the screen

        def make_message(self, nickname: str, text: str) -> dict:
            message = get_message_template()
            message["nickname"] = nickname
            message["text"] = text
            message["time"] = datetime.now().strftime('%H:%M:%S')
            return message

        # make_exit() gets a message template dict and makes exit message, recognized by server

        def make_exit(self) -> dict:
            message = get_message_template()
            message["action"] = "exit"
            message["time"] = datetime.now().strftime('%H:%M:%S')
            return message

    # GUI class unites all the methods, connected to creating and operating the messenger gui

    class GUI:

        def __init__(self, nickname):
            self.input_queue = Queue()
            self.output_queue = Queue()
            self.root = Tk()
            self.root.geometry('500x440+300+200')
            self.root.resizable(False, False)
            self.root.title("Radiogram")
            self.nickname = nickname

        def run(self):
            self.start_thread()
            self.render_start_screen()
            self.root.mainloop()

        def start_thread(self):
            p1 = Thread(target=self.print_message, daemon=True)
            p1.start()

        def render_start_screen(self):
            label = Label(self.root, text='Radiogram v 1.0')
            label.place(x=200, y=100, width=100)
            button_sign_up = Button(self.root, text='Sign up', bg='grey', fg='black', font='arial 14',
                                    command=self.render_sign_up_screen)
            button_sign_up.place(x=200, y=135, width=100, height=50)
            button_sign_in = Button(self.root, text='Sign in', width=8, height=2, bg='grey', fg='black',
                                    font='arial 14', command=self.render_sign_in_screen)
            button_sign_in.place(x=200, y=190, width=100, height=50)
            button_exit = Button(self.root, text='Exit', bg='grey', fg='black', font='arial 14', command=self.exit)
            button_exit.place(x=200, y=245, width=100, height=50)

        def render_sign_in_screen(self):
            self.clear_screen()
            label = Label(self.root, text='Sign up', font="arial 16")
            label.place(x=200, y=40, width=100)

            label = Label(self.root, text='Enter your login: ', font="arial 14")
            label.place(x=150, y=80, width=200)

            entry_login = Entry(self.root, font="arial 14")
            entry_login.place(x=150, y=120, width=200, height=30)

            label = Label(self.root, text='Enter your password: ', font="arial 14")
            label.place(x=150, y=160, width=200)

            entry_password = Entry(self.root, font="arial 14", show="*")
            entry_password.place(x=150, y=200, width=200, height=30, )

            button_continue = Button(self.root, text="Continue", font="arial 14", bg="grey", fg="black")
            button_continue.place(x=150, y=250, width=200, height=50)

        def render_sign_up_screen(self):
            self.clear_screen()

            label = Label(self.root, text='Sign up', font="arial 16")
            label.place(x=150, y=20, width=200)

            label = Label(self.root, text='Enter your login: ', font="arial 14")
            label.place(x=150, y=60, width=200)

            entry_login = Entry(self.root, font="arial 14")
            entry_login.place(x=150, y=100, width=200, height=30, )

            label = Label(self.root, text='Enter your password: ', font="arial 14")
            label.place(x=150, y=140, width=200)

            entry_password = Entry(self.root, font="arial 14")
            entry_password.place(x=150, y=180, width=200, height=30, )

            label = Label(self.root, text='Repeat your password: ', font="arial 14")
            label.place(x=150, y=220, width=200)

            entry_password_verify = Entry(self.root, font="arial 14", )
            entry_password_verify.place(x=150, y=260, width=200, height=30, )

            label = Label(self.root, text='Enter your email: ', font="arial 14")
            label.place(x=150, y=300, width=200)

            entry_mail = Entry(width=100, font="arial 14")
            entry_mail.place(x=150, y=340, width=200, height=30, )

            button_continue = Button(self.root, text="Continue", font="arial 14", bg="grey", fg="black",
                                     command=self.render_chat_screen)
            button_continue.place(x=150, y=380, width=200, height=50)

        def render_chat_screen(self):
            self.clear_screen()
            chat_output = Text(self.root, font='Arial 14', wrap=WORD, name="output")
            chat_output.place(x=5, y=5, width=490, height=340)

            chat_input = Text(self.root, font='Arial 14', wrap=WORD, name="input")
            chat_input.place(x=5, y=350, width=400, height=85)

            button_send = Button(self.root, text="Send", font="arial 14", bg="grey", fg="black",
                                 command=self.send_message)
            button_send.place(x=410, y=350, width=90, height=85)

        def send_message(self):
            output_frame = self.root.nametowidget("input")
            text = output_frame.get(1.0, END)

            text = self.cut_text(text)

            if text is None:
                return

            self.root.nametowidget("output").insert(END, f"{self.nickname} -> {text}")

            output_frame.delete(1.0, END)

            self.input_queue.put(text)

        def print_message(self) -> None:
            while True:
                try:
                    output_frame = self.root.nametowidget("output")
                    try:
                        message = self.output_queue.get()
                        output_frame.insert(END, f"{message['nickname']} -> {message['text']}")
                    except IndexError:
                        pass
                except KeyError:
                    pass

        def clear_screen(self):
            widget_list = self.root.place_slaves()

            for each in widget_list:
                each.destroy()

        # cut_text() removes all \n from start and end of the text, entered by user, and adds an \n at the end

        def cut_text(self, text: str):
            start_index = 0
            end_index = len(text) - 1

            while start_index < end_index:
                if text[start_index] != '\n':
                    break
                start_index += 1

            while end_index > start_index:
                if text[end_index] != '\n':
                    break
                end_index -= 1

            if start_index == end_index:
                return None

            text = text[start_index: end_index + 1] + '\n'

            return text

        def exit(self):
            self.root.destroy()


client = Client()

client.run()

