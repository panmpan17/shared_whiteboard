from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Lock, Thread
from random import randint
from time import sleep

import json
import requests
import logging

import argparse
import sys
import os

# load restful api auth username and password
# file "PASSWORD.py" will be ignore by github
from PASSWORD import USERNAME, PASSWORD
AUTH = requests.auth.HTTPBasicAuth(USERNAME, PASSWORD)
ONLINE_RESTAPI_URL = "http://michael628.pythonanywhere.com/api/"
OFFLINE_RESTAPI_URL = "http://localhost:8000/api/"

from encode import varify_code

restapi_url = None

runing = True
boards = {}
clients = {}
address_2_board = {}
BOARD = "board.text"

GET = "GET"
POST = "POST"
PUT = "PUT"
NEWBOARD = "NEWBOARD"
CREATEPREMIUMBOARD = "CREATEPREMIUMBOARD"

UNDO = "UNDO"
REDO = "REDO"

def encode(key, string):
    encoded_chars = []
    for i, c in enumerate(string):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(c) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return base64.urlsafe_b64encode(encoded_string.encode())

def random_code():
    return "".join([chr(randint(65, 90)) for _ in range(6)])

class Header:
    def __init__(self):
        self.method = None
        self.args = {}

    def __repr__(self):
        return f"{self.method}\n{self.args}"

    def __getitem__(self, key):
        return self.args[key]

    def has(self, key):
        return key in self.args

class Board:
    def __init__(self, layer_num=5):
        self.bg = []
        self.layers = []
        self.undos = []
        self.layer_num = 5

        for i in range(layer_num):
            self.layers.append(None)

    def new_stroke(self, stroke):
        self.layers.append(stroke)
        last_stroke = self.layers.pop(0)
        if last_stroke != None:
            self.bg.append(last_stroke)

    def undo(self):
        self.layers.insert(0, None)
        self.undos.append(self.layers.pop())

    def redo(self):
        self.layers.append(self.undos.pop())
        return self.layers[-1]

    def layers_string(self):
        string = ""

        for layer in self.layers:
            if layer == None:
                string += "|"
                continue
            string += layer + "|"

        return string

    def bg_string(self):
        string = ""

        for layer in self.bg:
            if layer == None:
                string += "|"
                continue
            string += layer + "|"

        return string

class SimpleChat(WebSocket):
    def __init__(self, server, sock, address, boards_limit=4, user_per_board=3):
        super().__init__(server, sock, address)

        self.verifing = {}
        self.lock = Lock()
        self.boards_limit = boards_limit
        self.user_per_board = user_per_board

    def parse(self, text):
        header = Header()
        args_text = text.split("&")

        for i in args_text:
            equl = i.find("=")
            key = i[:equl]
            value = i[equl + 1:]

            if key == "method":
                header.method = value
            else:
                header.args[key] = value

        return header

    def make_header(self, args):
        header = []

        for key, value in args.items():
            header.append(f"{key}={value}")

        return "&".join(header)

    def handleMessage(self):
        try:
            header = self.parse(self.data)
        except:
            return
        address = "%s:%s" % self.address

        # create free white board for system
        if header.method == NEWBOARD:
            if len(boards) < self.boards_limit:
                board_id = random_code()
                while board_id in boards:
                    board_id = random_code
                boards[board_id] = Board()
                clients[board_id] = []

                args = {
                    "method": NEWBOARD,
                    "success": "True",
                    "board_id": board_id
                }

                header = self.make_header(args)
                self.sendMessage(header)
                return
            else:
                args = {
                    "method": NEWBOARD,
                    "success": "False",
                }

                header = self.make_header(args)
                self.sendMessage(header)
                return

        elif header.method == CREATEPREMIUMBOARD:
            code = header.args["code"]
            if varify_code(code):
                self.sendMessage("A")
                return

            args = {
                "success": "False",
                "reason": "wrong code",
            }
            self.sendMessage(self.make_header(args))
            return

        # check is user been verifing
        if address in self.verifing:
            if header.has("board_id"):
                board_id = header["board_id"]
                if board_id in boards:
                    if len(clients[board_id]) >= self.user_per_board:
                        args = {
                            "method": GET,
                            "success": "False",
                            "reason": "too many people",
                        }
                        self.sendMessage(self.make_header(args))
                        return

                    self.verifing[address]["verify"] = True
                    logging.warning(address + " passed verify")

                    clients[board_id].append(self.verifing[address]["conn"])
                    address_2_board[address] = board_id
                    board = boards[board_id]

                    args = {
                        "method": GET,
                        "success": "True",
                        "layer_num": board.layer_num,
                        "bg": board.bg_string(),
                        "layers": board.layers_string(),
                    }
                    self.sendMessage(self.make_header(args))
            return

        # if header.method == GET:
        #     args = {
        #         "method": GET,
        #                 "success": "True",
        #         "layer_num": board.layer_num,
        #         "bg": board.bg_string(),
        #         "layers": board.layers_string(),
        #     }
        #     self.sendMessage(self.make_header(args))
        #     return

        if header.method == POST:
            if (not header.has("board_id")) or (not header.has("stroke")):
                return
            board_id = header["board_id"]
            board = boards[board_id]
            board.new_stroke(header["stroke"])
            board.undos.clear()

            args = {
                "method": POST,
                "stroke": header["stroke"]
            }

            header = self.make_header(args)
            if board_id in clients:
                for client in clients[board_id]:
                    client.sendMessage(header)
            return

        elif header.method == PUT:
            if not header.has("board_id"):
                return
            board = boards[header["board_id"]]
            if header.args["action"] == UNDO:
                if board.layers.count(None) == board.layer_num:
                    return
                board.undo()

                args = {
                    "method": PUT,
                    "action": UNDO,
                }

                header = self.make_header(args)
                for client in clients:
                    client.sendMessage(header)
                return
            elif header.args["action"] == REDO:
                if len(board.undos) == 0:
                    return
                stroke = board.redo()

                args = {
                    "method": POST,
                    "stroke": stroke,
                }

                header = self.make_header(args)
                for client in clients:
                    client.sendMessage(header)
                return

    def handleConnected(self):
        address = "%s:%s" % self.address
        logging.warning(address + ' connected waitng for verify')

        self.verifing[address] = {
            "conn": self,
            "verify": False,
            }
        t = Thread(target=self.automatic_disconnect, args=(address, ))
        t.start()

    def automatic_disconnect(self, address):
        sleep(3)
        if not self.verifing[address]["verify"]:
            self.verifing[address]["conn"].close()
            logging.warning(address + " failed verify")
        self.verifing.pop(address)

    def handleClose(self):
        address = "%s:%s" % self.address
        logging.warning(address + " disconnect")

        if address in address_2_board:
            for conn in clients[address_2_board[address]]:
                conn_address = "%s:%s" % conn.address
                if address == conn_address:
                    clients[address_2_board[address]].remove(conn)
                    break
            address_2_board.pop(address)

def delete_emptyroom():
    while runing:
        sleep(120)
        remove_board = []
        for board_id, client in clients.items():
            if len(client) == 0:
                remove_board.append(board_id)
        for board_id in remove_board:
            board = boards.pop(board_id)
            clients.pop(board_id)

            r = requests.post(restapi_url + "board/", auth=AUTH, json={
                "layers": board.layers_string(),
                "background": board.bg_string(),
                })

            logging.warning(f"Board {board_id} has been removed")

if __name__ == "__main__":
    logging.warning("Starting server ....")
    parser = argparse.ArgumentParser(description='Start up Socket Server')
    parser.add_argument('-port', type=int, default=21085, required=False)
    parser.add_argument('-online', type=bool, default=False, required=False)
    args = parser.parse_args()

    port = args.port
    if args.port > 65000:
        port = 21085

    if args.online:
        restapi_url = ONLINE_RESTAPI_URL
    else:
        restapi_url = OFFLINE_RESTAPI_URL
    logging.warning("Rstful Api url: " + restapi_url)

    server = SimpleWebSocketServer("0.0.0.0", port, SimpleChat)
    logging.warning("Port: " + str(port))
    try:
        t = Thread(target=delete_emptyroom)
        t.start()
        server.serveforever()
    except KeyboardInterrupt:
        runing = False
        server.close()
        sys.exit()