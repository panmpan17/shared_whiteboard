import asyncio
import websockets

@asyncio.coroutine
def hello(websocket, path):
    writer = websocket.writer

    addr = writer.get_extra_info('peername')
    print("connect with :", addr)
    while True:
        name = yield from websocket.recv()
        print("< {}".format(name))

        greeting = "Hello {}!".format(name)
        yield from websocket.send(greeting)
        print("> {}".format(greeting))

start_server = websockets.serve(hello, "localhost", 28689)

loop = asyncio.get_event_loop()
server = loop.run_until_complete(start_server)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.close()