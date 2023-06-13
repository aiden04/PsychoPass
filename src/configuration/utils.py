import json
import os
import base64
from cryptography.fernet import Fernet
from src.configuration.jsonManagement import JsonPath

tmd1 = './src/configuration/TMD1'
tmd2 = './src/configuration/TMD2'
tmd3 = './src/configuration/TMD3'
tmd4 = './src/configuration/TMD4'

ttk_style = 'clam'

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

def decryptString(string):
    key = KEY()
    f = Fernet(key)
    decrypted = f.decrypt(string).decode()
    return decrypted

def keyGen():
    key = Fernet.generate_key()
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

def list(file_path):
    if os.path.getsize(file_path) > 0:
        with open(file_path, 'r') as f:
            data = f.read()
            data = decryptString(data)
            data = f'''
    =====================================
            {data}
    =====================================
            '''
            return data
    if os.path.getsize(file_path) == 0:
        data = ''
        return data
    
def writingTMD(username, email, password, website):
    key = KEY()
    UserName = f"Username: {username}"
    Email = f"Email: {email}"
    Password = f"Password: {password}"
    WebSite = f"Website: {website}"
    data = f'''
    {UserName}
    {Email}
    {Password}
    {WebSite}
    '''
    data = encryptString(data, key)
    with open(tmd2, 'ab') as TMD:
        TMD.write(data)

def clearTMD(TMD):
    if os.path.getsize(TMD) == 0:
        data = 'There are no passwords to clear.'
        return data
    if os.path.getsize(TMD) > 0:
        with open(TMD, 'w') as f:
            f.truncate(0)
            data = 'Passwords Cleared!'
            return data
