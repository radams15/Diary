import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class Crypt:
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        old=raw
        try:
            raw += "!"
            raw = self._pad(raw)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            encoded = base64.b64encode(iv + cipher.encrypt(raw.encode())).decode()
            return encoded
        except Exception as e:
            print(e)
            return old

    def decrypt(self, enc):
        old=enc
        try:
            enc = base64.b64decode(enc.encode())
            iv = enc[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decoded = self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

            if decoded and decoded[-1] == "!":
                return decoded[0:-1]
            else:
                return None
        except Exception as e:
            print(e)
            return old


    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

if __name__ == '__main__':
    c = Crypt("pafaf")

    a = "hello"
    b = c.encrypt(a)
    d = c.decrypt(b)

    print(a, b, d)