import json
import os
import base64
from cryptography.fernet import Fernet
from src.configuration.jsonManagement import JsonPath

tmd1 = './src/configuration/TMD1'
tmd2 = './src/configuration/TMD2'
tmd3 = './src/configuration/TMD3'
tmd4 = './src/configuration/TMD4'

def keyCheck():
    with open(JsonPath) as JsonFile:
        data = json.load(JsonFile)
        if data.get('Key'):
            return True
        else:
            with open(tmd3, 'wb') as TMD:
                key = keyGen()
                TMD.write(key)
            data['Key'] = True
            with open(JsonPath, 'w') as JsonFile:
                json.dump(data, JsonFile)
            return False
        
def encryptString(string, key):
    f = Fernet(key)
    encrypted = f.encrypt(string.encode())
    return encrypted

def decryptString(string, key):
    f = Fernet(key)
    decrypted = f.decrypt(string).decode()
    return decrypted

def keyGen():
    key = Fernet.generate_key()
    print(key)
    return key

def KEY():
    if os.path.isfile(tmd3):
        with open(tmd3, 'r') as TDM:
            key = TDM.read()
            return key.strip()

def saveLogin(login):
    with open(tmd1, 'wb') as f:
        f.write(login)

def savedLogin():
    with open(tmd1, 'r') as f:
        login = f.read()
        return login

