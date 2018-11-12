import json
from threading import Thread
from datetime import datetime
from socket import socket
from multiprocessing import Queue
from log import client_log_config

ADDRESS = "localhost"
PORT = 10000
MESSAGE_SIZE = 1024
LISTEN_QUEUE_LEN = 10
SERVER_TIMEOUT = 0


class Client:

    def __init__(self):
        self.s = socket()
        self.nickname = ""
        self.receive_queue = Queue()
        self.send_queue = Queue()

    def message_template(self, action):
        return {"action": "",
                "nickname": self.nickname,
                "text": ""}

    def run(self) -> None:
        client_log_config.logger.info("Initialization")
        self.nickname = input()
        self.connect()
        self.send_presence()
        response = json.loads(self.s.recv(MESSAGE_SIZE).decode("utf-8"))
        if response["response"] == 200:
            client_log_config.logger.info("Connection successful")
            self.run_threads()
            while True:
                message = self.receive_queue.get()
                print(f"{message['nickname']} -> {message['text']}")
        else:
            self.s.close()
            client_log_config.logger.critical("Connection error")
            raise Exception("Connection error")

    def run_threads(self) -> None:
        try:
            client_log_config.logger.info("Running threads")
            send_loop = Thread(target=self.send_message, daemon=True).start()
            get_loop = Thread(target=self.get_message, daemon=True).start()
        except:
            client_log_config.logger.critical("Threads running error")

    def connect(self) -> None:
        try:
            client_log_config.logger.info("Connecting " + ADDRESS)
            self.s.connect((ADDRESS, PORT))
        except ConnectionRefusedError:
            client_log_config.logger.critical("Connection error")
            quit(-1)

    def close(self) -> None:
        self.s.send(json.dumps({"action": "exit"}).encode("utf-8"))
        self.s.close()
        client_log_config.logger.info("Exit")
        quit(1)
        client_log_config.logger.critical("Exit error")
        quit(-1)

    def send_presence(self) -> None:
        client_log_config.logger.info("Sending presence")
        presence = {
            "action": "presence",
            "time": datetime.now().strftime('%H:%M:%S'),
            "nickname": self.nickname
        }
        self.s.send(json.dumps(presence).encode("utf-8"))

    def send_message(self) -> None:
        while True:
            text = input(f"{self.nickname} -> ")
            try:
                if text == "exit":
                    self.close()

                message = self.message_template("message")
                message["text"] = text
                self.s.send(json.dumps(message).encode("utf-8"))
            except ConnectionError:
                client_log_config.logger.critical("Message sending error")
                quit(-1)

    def get_message(self) -> None:
        while True:
            try:
                self.receive_queue.put(json.loads(self.s.recv(MESSAGE_SIZE).decode("utf-8")))
                client_log_config.logger.info("Message recieved")
            except ConnectionError:
                client_log_config.logger.critical("Message receiving error")
                quit(-1)


client = Client()

client.run()

