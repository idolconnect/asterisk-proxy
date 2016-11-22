import rijndael
import base64
import json

def decrypt_cbc(s, iv, key):
    p = b"".join(rijndael.decrypt(key, bytes(s[i:i+len(iv)])) for i in range(0, len(s), len(iv)))
    return bytes((iv+s)[i] ^ p[i] for i in range(len(p)))

def remove(s):
    ret = ""
    for c in s:
        if ord(c) >= 31:
            ret += c
    return ret

def decrypt(encrypted_body):
    key = "XzPetwRQtSj7btjf24LJIahPhcLGQZCi".encode()
    step1 = encrypted_body.replace("*", "+").replace(",", "/").replace("-", "=")
    step2 = base64.b64decode(step1.encode()).decode()
    step3 = base64.b64decode(step2[16:].encode())
    step4 = step2[0:16].encode()
    step5 = decrypt_cbc(step3, step4, key).decode()
    step6 = remove(step5)
    return step6