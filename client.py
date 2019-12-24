import socket
import random
import json


class DH_client:
    p = None
    g = None
    a = None
    A = None
    _B = None
    K = None

    def __init__(self, boolean, p=None, g=None):
        keys = None
        if boolean:
            keys = self.read_keys()
        if (keys):
            self.A = keys['public']
            self.K = keys['private']
            self.p = keys['p']
            self.g = keys['g']
            self.a = keys['a']
            self.new = False
        else:
            self.p = p
            self.g = g
            self.a = random.randint(1, 10000)
            self.A = self.g ** self.a % self.p
            self.new = True

    @property
    def B(self):
        return self._B

    @B.setter
    def B(self, val):
        self._B = val
        self.K = self.B ** self.a % self.p

    def encrypt_message(self, message):
        encrypted_message = ""
        for c in message:
            encrypted_message += chr(ord(c) + self.K)
        return encrypted_message

    def decrypt_message(self, encrypted_message):
        decrypted_message = ""
        for c in encrypted_message:
            decrypted_message += chr(ord(c) - self.K)
        return decrypted_message

    def save_keys(self, filename='client.json'):
        with open(filename, 'w') as json_file:
            json.dump({
                'public': self.A,
                'private': self.K,
                'p': self.p,
                'g': self.g,
                'a': self.a,
            }, json_file)

    @staticmethod
    def read_keys(filename='client.json'):
        try:
            with open(filename, 'r') as json_file:
                keys = json.loads(json_file)
                return keys
        except FileNotFoundError:
            return None


sock = socket.socket()
k = False
while not k:
    try:
        print("Host:")
        host = input()
        if host == "":
            host = 'localhost'
        print("Port:")
        port = input()
        if port == "":
            port = 9090
        sock.connect((host, int(port)))
        data = sock.recv(1024).decode()
        if data == 'old':
            dh_client = DH_client(True)
        else:
            p, g, B = [int(i) for i in data.split()]
            dh_client = DH_client(False, p, g)
            dh_client.B = B

            sock.send(str(dh_client.A).encode())
        print("Save keys??? (y/n)")
        while True:
            msg = input().lower()
            if msg == 'y':
                dh_client.save_keys()
                sock.send("save".encode())
            elif msg == 'n':
                break
        print('Enter or exit')
        msg = input()
        while msg != 'exit':
            sock.send(dh_client.encrypt_message(msg).encode())
            print(dh_client.decrypt_message(sock.recv(1024).decode()))
            msg = input()
        k = True
    except KeyboardInterrupt:
        break
sock.close()