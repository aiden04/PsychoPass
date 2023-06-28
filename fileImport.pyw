import os
import sys
import getpass
import json
from cryptography.fernet import Fernet
import PySimpleGUI as sg

script_path = os.path.abspath(sys.argv[0])
root = os.path.dirname(script_path)
user = getpass.getuser()
icon = f'{root}/icon.ico'
logo = f'{root}/logo.png'
ttk_style = 'clam'
appdata_path = os.path.join(os.environ['LOCALAPPDATA'], 'PsychoPass')
os.makedirs(appdata_path, exist_ok=True)
tmd1 = f'{appdata_path}/TMD1.pyp'
tmd2 = f'{appdata_path}/TMD2.pyp'
tmd3 = f'{appdata_path}/TMD3.pyp'
JsonPath = f'{appdata_path}/settings.json'

if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    sg.popup('Invalid File Path.')

class Json:
        def Read(Variable):
            try:
                with open(JsonPath, 'r') as f:
                    file = json.load(f)
                    Value = file.get(Variable)
                    return Value
            except FileNotFoundError:
                sg.popup('Settings File not found.', icon=icon, title='PsychoPass')
                sys.exit()

class Cryptography:
    def Encrypt(input):
        try:
            with open(tmd3, 'r') as f:
                key = f.read()
                f.close()
            fern = Fernet(key)
            data = fern.encrypt(input.encode())
            return data
        except Exception as e:
            sg.popup('Encryption key either Missing or Invalid.\n' + str(e), icon=icon, title='PsychoPass')
            sys.exit()
    def Decrypt(input):
        try:
            with open(tmd3, 'r') as f:
                key = f.read()
                f.close()
            fern = Fernet(key)
            data = fern.decrypt(input)
            return data.decode()
        except Exception as e:
            sg.popup('Encryption Key either Missing or Invalid.\n' + str(e), icon=icon, title='PsychoPass')
            sys.exit()
    def ExternalDecryption(Input, Key):
        fern = Fernet(Key)
        data = fern.decrypt(Input)
        return data

class TMD:
    def Read(TMD, all_lines=False):
        if all_lines is False:
            try:
                with open(TMD, 'r') as f:
                    file = f.read()
                    f.close()
                    return file
            except FileNotFoundError:
                sg.popup('TMD File not found.', icon=icon, title='PsychoPass')
                sys.exit()
        if all_lines is True:
            try:
                LineVariables = {}
                with open(TMD, 'rb') as f:
                    lines = f.readlines()
                decrypted_lines = []
                for i, line in enumerate(lines):
                    VariableName = f'line{i + 1}'
                    LineVariables[VariableName] = line.strip().decode()
                    LineVariables[VariableName] = Cryptography.Decrypt(LineVariables[VariableName])
                    decrypted_lines.append(LineVariables[VariableName])
                data = '\n\n  ====================================================\n'.join(decrypted_lines)
                data = f'''
                  ====================================================
                    {data}
                  ====================================================
            '''
                return data
            except Exception as e:
                sg.popup('Error:' + str(e))
    def Import(key_path):
        try:
            LineVariables = {}
            DecryptedLines = []
            with open(key_path) as k:
                key = k.read()
            with open(file_path, 'r') as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                VariableName = f'line{i + 1}'
                LineVariables[VariableName] = line.strip()
                DecryptedLine = Cryptography.ExternalDecryption(LineVariables[VariableName], key)
                DecryptedLines.append(DecryptedLine.decode())
            decrypted_data = '\n\n  ====================================================\n'.join(DecryptedLines)
            print(f'Decrypted: {decrypted_data}')
            encrypted_data = Cryptography.Encrypt(decrypted_data).decode()
            print(f'Encrypted: {encrypted_data}')
            with open(tmd2, 'a') as f:
                f.write(encrypted_data + '\n')
        except Exception as e:
            sg.popup('Error: ' + str(e))

class Authentication:
    def AuthenticateLogin(input):
        try:
            Credentials = TMD.Read(tmd1)
            Credentials = Cryptography.Decrypt(Credentials)
            if input == Credentials:
                return True
            else:
                return False
        except FileNotFoundError:
            sg.popup('TMD File not found.', icon=icon, title='PsychoPass')
            sys.exit()

if os.path.exists(JsonPath):
    Theme = Json.Read('Theme')
else:
    Theme = 'SystemDefault'

class PsychoPass:
    def Authenticate(type=1):
        layout = [
            [sg.Image(logo)],
            [sg.Text('Please Verify Credentials.', font=('Helvetica', 20), size=(20, 1))],
            [sg.Text('Username:', font=('Helvetica'), size=(10, 1)), sg.Input(key='-USERNAME-', size=(20, 1))],
            [sg.Text('Password:', font=('Helvetica'), size=(10, 1)), sg.Input(key='-PASSWORD-', size=(20, 1))],
            [sg.Button('Login', size=(10, 1)), sg.Button('Close', size=(10, 1))]
        ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', margins=(10, 10), use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Login':
                Credentials = values['-USERNAME-'] + values['-PASSWORD-']
                CheckLogin = Authentication.AuthenticateLogin(Credentials)
                if CheckLogin is True:
                    if type == 1:
                        window.close()
                        PopupLayout = [[sg.T('This will delete all saved data for PsychoPass. Are you sure you want to continue?', font=('Helvetica'), size=(6, 1))],[sg.B('Yes'), sg.B('No')]]
                        PopupWindow = sg.Window('PsychoPass', PopupLayout)
                        while True:
                            event, values = PopupWindow.read()
                            if event == 'Yes':
                                PopupWindow.close()
                                TMD.FactoryReset()
                            if event == 'No':
                                PopupWindow.close()
                                PsychoPass.Options()
                            if event == sg.WIN_CLOSED:
                                sys.exit()
                        PopupWindow.close()
                    if type == 2:
                        window.close()
                        PsychoPass.CreateAccount(type=2)
                    if type == 3:
                        window.close()
                        PsychoPass.ExportTMD(type=1)
                    if type == 4:
                        window.close()
                        PsychoPass.ExportTMD(type=2)
                    if type == 5:
                        window.close()
                        PsychoPass.ImportTMD()
                if CheckLogin is False:
                    sg.popup('Invalid Credentials.')
            if event == sg.WIN_CLOSED or event == 'Close':
                sys.exit()
        window.close()
    def ImportTMD():
        layout = [
            [sg.Image(logo)],
            [sg.Text('Please select Key file.')],
            [sg.Text(f'Selected Path: {file_path}')],
            [sg.Text('Key'), sg.Input(key='-KEYINPUT-'), sg.FileBrowse(file_types=[('PsychoPass File', '*.pyp')])],
            [sg.Button('Import'), sg.Button('Close')]
            ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Import':
                KeyInput = values['-KEYINPUT-']
                TMD.Import(KeyInput)
                sg.popup('Successfully Imported!')
            if event == 'Close':
                sys.exit()
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()

PsychoPass.Authenticate(type=5)