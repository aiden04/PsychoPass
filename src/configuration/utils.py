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

def decryptString(string, key):
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
    key = KEY()
    decrypted_lines = []

    try:
        with open(file_path, 'rb') as file:
            data = file.read().decode()

        lines = data.splitlines()

        for line in lines:
            decrypted_line = decryptString(line.strip(), key)
            decrypted_line = decrypted_line.strip("\n[]'")
            decrypted_lines.append(decrypted_line)

    except FileNotFoundError:
        return None

    return decrypted_lines
    
def writingTMD(username, email, password, website, key):
    data = f'=============================================================\n' + f'        Email: {email}' + f'        Username: {username}\n' +f'         Password: {password}' + f'        Website: {website}\n' + '============================================================='
    
    serialized_data = data
    encrypted_data = encryptString(serialized_data, key).decode()
    with open(tmd2, 'a') as TMD:
        TMD.write(encrypted_data + '\n')

    return "Saved!"

def cleanUpOutputText(output_text):
    cleaned_lines = []
    for line in output_text:
        line = line.strip("=\n ")
        line = line.replace("Email:", "Email: ").replace("Username:", "Username: ")
        line = line.replace("Password:", "Password: ").replace("Website:", "Website: ")
        cleaned_lines.append(line)
    cleaned_text = "\n".join(cleaned_lines)
    return cleaned_text
