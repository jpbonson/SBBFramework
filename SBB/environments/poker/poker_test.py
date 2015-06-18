import socket

class PokerPlayer():

    def __init__(self, port):
        self.socket = socket.socket()
        self.socket.connect(("localhost", port))

    def run(self):
        self.socket.send("VERSION:2.0.0\r\n")
        print self.socket.recv(256)
        self.socket.close()

if __name__ == "__main__":
    PokerPlayer().run()