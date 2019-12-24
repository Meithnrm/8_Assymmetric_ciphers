import socket
import random
from functools import wraps
import json

def cache_gcd(f):
    cache = {}

    @wraps(f)
    def wrapped(a, b):
        key = (a, b)
        try:
            result = cache[key]
        except KeyError:
            result = cache[key] = f(a, b)
        return result

    return wrapped


@cache_gcd
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


class DH:

    p = None
    g = None
    a = None
    A = None
    _B = None
    K = None

    def __init__(self, boolean):
        keys = None
        if boolean:
            keys = self.read_keys()
        if(keys):
            self.A = keys['public']
            self.K = keys['private']
            self.p = keys['p']
            self.g = keys['g']
            self.a = keys['a']
            self.new = False
        else:
            self.p = random.choice(DH.generic(10000))
            self.g = random.choice(DH.simple_g(DH.prim_roots(self.p)))
            self.a = random.randint(1, 100000)
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

    @staticmethod
    def simple_g(g_list):
        return [i for i in g_list if DH.is_prime(i)]

    @staticmethod
    def generic(n):
        return [i for i in range(100, n + 1) if DH.is_prime(i) and DH.is_prime((i - 1) // 2)]

    @staticmethod
    def is_prime(n):
        if n == 2 or n == 3:
            return True
        for i in range(2, n // 2 + 1):
            if n % i == 0:
                break
        else:
            return True
        return False

    @staticmethod
    def prim_roots(modulo):
        coprime_set = {num for num in range(1, modulo) if gcd(num, modulo) == 1}
        return [g for g in range(1, modulo) if coprime_set == {pow(g, powers, modulo)
                                                               for powers in range(1, modulo)}]

    @property
    def string_keys(self):
        return f"{self.p} {self.g} {self.A}"

    def save_keys(self, filename='server.json'):
        with open(filename, 'w') as json_file:
            json.dump({
                'public': self.A,
                'private': self.K,
                'p': self.p,
                'g': self.g,
                'a': self.a,
            }, json_file)

    @staticmethod
    def read_keys(filename='server.json'):
        try:
            with open(filename, 'r') as json_file:
                keys = json.loads(json_file)
                return keys
        except FileNotFoundError:
            return None


port = 9090
sock = socket.socket()
try:
    sock.bind(('', port))
except OSError:
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    print(f"use port {port}")

print("If you want new keys enter 'new'")
msg = input()
if msg == "new":
    dh = DH(False)
else:
    dh = DH(True)
print("Ready to work")


sock.listen(0)

conn, addr = sock.accept()
print(addr)
msg = ''

if dh.new:
    conn.send(dh.string_keys.encode())
    B = int(conn.recv(1024).decode())
    dh.B = B
else:
    conn.send("old".encode())

while True:
    data = conn.recv(1024)
    if not data:
        break
    if data.decode() == "save":
        dh.save_keys()
    decrypted = dh.decrypt_message(data.decode())
    print(decrypted)
    conn.send(dh.encrypt_message(decrypted.upper()).encode())

conn.close()
sock.close()