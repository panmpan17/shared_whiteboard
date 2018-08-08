from random import randint
from datetime import datetime

import json
import base64

# load encryption key
# file "CODE.json" will be ignore by github
try:
    KEYS = json.load(open("KEYS.json"))
except:
    KEYS = json.load(open("Websocket/KEYS.json"))

def encode(key, string):
    encoded_chars = []
    for i, c in enumerate(string):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(c) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return base64.urlsafe_b64encode(encoded_string.encode()).decode()

def new_code():
    index = randint(0, len(KEYS) - 1)
    key = KEYS[index]

    now = datetime.utcnow()
    now_string = now.strftime("%Y%m%d%H")
    code = encode(key, now_string)
    
    index = str(index)
    if len(index) == 1:
        index = "0" + index
    return index + code

def varify_code(code):
    index = code[:2]
    index = int(index)
    code = code[2:]
    key = KEYS[index]

    now = datetime.utcnow()
    now_string = now.strftime("%Y%m%d%H")
    new_code = encode(key, now_string)
    return code == new_code