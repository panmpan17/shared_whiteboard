from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Lock
from time import sleep
import sys
import os

BOARD = "board.text"
clients = []

GET = "GET"
POST = "POST"
PUT = "PUT"

UNDO = "UNDO"
REDO = "REDO"

class Header:
    def __init__(self):
        self.method = None
        self.args = {}

    def __repr__(self):
        return f"{self.method}\n{self.args}"

    def __getitem__(self, key):
        return self.args[key]

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
    def __init__(self, server, sock, address):
        super().__init__(server, sock, address)

        self.lock = Lock()

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

        if header.method == GET:
            args = {
                "method": GET,
                "layer_num": board.layer_num,
                "bg": board.bg_string(),
                "layers": board.layers_string(),
            }
            self.sendMessage(self.make_header(args))
            return

        elif header.method == POST:
            board.new_stroke(header["stroke"])
            board.undos.clear()

            args = {
                "method": POST,
                "stroke": header["stroke"]
            }

            header = self.make_header(args)
            for client in clients:
                client.sendMessage(header)
            return

        elif header.method == PUT:
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
        print(self.address, 'connected')
        # for client in clients:
        #     client.sendMessage(self.address[0] + u' - connected')
        clients.append(self)

    def handleClose(self):
        clients.remove(self)
        print(self.address, 'closed')
        # for client in clients:
        #     client.sendMessage(self.address[0] + u' - disconnected')

if __name__ == "__main__":
    board = Board()
    server = SimpleWebSocketServer('0.0.0.0', 21085, SimpleChat)
    try:
        server.serveforever()
    except KeyboardInterrupt:
        server.close()
        sys.exit()