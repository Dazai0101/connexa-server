# connexa-server/encryption.py
from cryptography.fernet import Fernet

# Same key as client.py
KEY = b'VhrmID9iBRHqX7k2HFuIXl9Arft7-2aNLZ8jv4Wjks8='
cipher = Fernet(KEY)

def decrypt_message(data: bytes) -> str:
    try:
        return cipher.decrypt(data).decode()
    except:
        return "[Decryption Error]"
