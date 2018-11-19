import json
from threading import Thread
from select import select
from socket import socket
from log import server_log_config
from configs import ADDRESS, PORT, MESSAGE_SIZE, LISTEN_QUEUE_LEN, SELECT_TIMEOUT


class Server:

    def __init__(self):
        self.s = socket()
        self.clients_list = []
        self.clients_dict = {}
        self.db_handler = self.DBHandler()
        self.id = 0

    def run(self) -> None:
        server_log_config.logger.info("Initialization")
        self.connect()

        Thread(target=self.get_clients, daemon=True).start()

        while True:
            client, addr = self.s.accept()
            if self.get_presense(client):
                self.clients_list.append(client)
                self.clients_dict.update({client: self.id})
                self.id += 1
                server_log_config.logger.info("Client connected")
                print(self.clients_list)

    def get_clients(self) -> None:
        server_log_config.logger.info("Reading clients")
        while True:
            try:
                readable, _, _ = select(self.clients_list, [], [], SELECT_TIMEOUT)
                if len(readable) > 0:
                    for client in readable:
                        self.read_socket(client)
            except:
                pass

    def connect(self) -> None:
        server_log_config.logger.info("Connecting")
        self.s.bind((ADDRESS, PORT))
        self.s.listen(LISTEN_QUEUE_LEN)

    def close(self) -> None:
        self.s.close()

    def get_presense(self, client: socket) -> bool:
        client.setblocking(True)
        message = json.loads(client.recv(MESSAGE_SIZE).decode("utf-8"))

        response = {
            "response": 400
        }

        if "action" in message and message["action"] == "presence":
            response = {
                "response": 200
            }

            server_log_config.logger.info("Connection accepted")

        else:
            server_log_config.logger.info("Connection denied")

        client.send(json.dumps(response).encode("utf-8"))
        return response["response"] == 200

    def read_socket(self, sender) -> None:
        client_id = self.clients_dict.get(sender)
        message = json.loads(sender.recv(MESSAGE_SIZE).decode("utf-8"))
        if message["action"] == "exit":
            self.clients_list.remove(sender)
            self.clients_dict.pop(sender)
            return

        for client in self.clients_list:
            if client_id != self.clients_dict.get(client):
                client.send(json.dumps(message).encode("utf-8"))

    class MessageHandler:
        def __init__(self):
            pass

    class DBHandler:
        def __init__(self):
            pass


server = Server()

server.run()

