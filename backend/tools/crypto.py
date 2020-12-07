import hashlib
import rsa
import time
import base64


def md5_encode(value: str) -> str:
    return hashlib.md5(value.encode(encoding='UTF-8')).hexdigest()


def rsa_encode(value: str) -> str:

    public_key = '''''' # your own rsa public key
    message = value + '`' + str(time.time() + 3600 * 10000)
    pubkey = rsa.PublicKey.load_pkcs1(public_key.encode())
    while True:
        crypto = rsa.encrypt(message.encode(), pubkey)
        res = (base64.b64encode(crypto)).decode('utf-8')
        if '+' not in res:
            break
    return res


def rsa_decode(encode):
    try:
        encode = base64.b64decode(encode)
        private_key = '''''' # your own rsa private key
        privkey = rsa.PrivateKey.load_pkcs1(private_key.encode())
        message = rsa.decrypt(encode, privkey).decode()
        # print(message)
    except Exception as e:
        # print(e)
        return ''
    return message.split('`')[0]


if __name__ == '__main__':
    print(rsa_decode('AS1MlH5LjmR3mBCmsIWLjDZvvQnQOMCZOPmIYAgEjbEdhE2/fWxLwIEsEeqyTFNsuAViOg83rbLXUZxGFbAqt=='))
