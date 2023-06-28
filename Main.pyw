import json
import os
import random
import string
import getpass
import shutil
import sys
import PySimpleGUI as sg
from cryptography.fernet import Fernet

appdata_path = os.path.join(os.environ['LOCALAPPDATA'], 'PsychoPass')
os.makedirs(appdata_path, exist_ok=True)
script_path = os.path.abspath(sys.argv[0])
root = os.path.dirname(script_path)
user = getpass.getuser()
icon = f'{root}/icon.ico'
logo = f'{root}/logo.png'
JsonPath = f'{appdata_path}/settings.json'
tmd1 = f'{appdata_path}/TMD1.pyp'
tmd2 = f'{appdata_path}/TMD2.pyp'
tmd3 = f'{appdata_path}/TMD3.pyp'
ttk_style = 'clam'

class Json:
    def PreLaunch():
        JsonDefault = {
            'Theme': 'SystemDefault'
        }
        if os.path.exists(JsonPath):
            return
        if not os.path.exists(JsonPath):
            with open(JsonPath, 'w') as f:
                json.dump(JsonDefault, f)
                f.close()
    
    def Read(Variable):
        try:
            with open(JsonPath, 'r') as f:
                file = json.load(f)
                Value = file.get(Variable)
                return Value
        except FileNotFoundError:
            sg.popup('Settings File not found.', icon=icon, title='PsychoPass')
            sys.exit()
        
    def Edit(Variable, Value):
        try:
            with open(JsonPath, 'r') as f:
                file = json.load(f)
            file[Variable] = Value
            with open(JsonPath, 'w') as f:
                json.dump(file, f, indent=4)
        except FileNotFoundError:
            sg.popup('Settings File not found.', icon=icon, title='PsychoPass')
            sys.exit

class Cryptography:
    def CreateKey():
        key = Fernet.generate_key()
        return key
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
    def GeneratePassword(MAX_LEN=12):
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(MAX_LEN))
        return password

class TMD:
    def Check():
        tmd1Present = os.path.isfile(tmd1)
        tmd2Present = os.path.isfile(tmd2)
        tmd3Present = os.path.isfile(tmd3)
        if not tmd1Present:
            with open(tmd1, 'w') as f:
                f.write('')
                f.close()
        if not tmd2Present:
            with open(tmd2, 'w') as f:
                f.write('')
                f.close()
        if not tmd3Present:
            with open(tmd3, 'wb') as f:
                key = Cryptography.CreateKey()
                f.write(key)
                f.close()
        else:
            pass
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
    def Import(file_path, key_path):
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
            encrypted_data = Cryptography.Encrypt(decrypted_data).decode()
            with open(tmd2, 'a') as f:
                f.write(encrypted_data + '\n')
        except Exception as e:
            sg.popup('Error: ' + str(e))


    def Write(TMD, input, open_type):
        try:
            if open_type == 'a':
                with open(TMD, 'a') as f:
                    f.write(input)
                    f.close()
            if open_type == 'w':
                with open(TMD, 'w') as f:
                    f.write(input)
                    f.close()
        except FileNotFoundError:
            sg.popup('TMD File not found.', icon=icon, title='PsychoPass')
    def Clear(TMD):
        try:
            if os.path.getsize(TMD) == 0:
                Error = "There are no passwords to clear."
                return Error
            if os.path.getsize(TMD) > 0:
                with open(TMD, 'w') as f:
                    f.truncate(0)
                    f.close()
                    file = 'Passwords Cleared!'
                    return file
        except FileNotFoundError:
            sg.popup('TMD File not found.', icon=icon, title='PsychoPass')
    def Export(tmd, OutPath):
        try:
            shutil.copy(tmd, OutPath)
            sg.popup('Data Successfully Exported!')
        except Exception as e:
            sg.popup('Error: ' + str(e))
    def FactoryReset():
        try:
            os.remove(tmd1)
            os.remove(tmd2)
            os.remove(tmd3)
            os.remove(JsonPath)
            sg.popup('All data has been reset. PsychoPass will now close.', icon=icon, title='PsychoPass', )
            sys.exit()
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
            [sg.Button('Login', size=(10, 1)), sg.Button('Back', size=(10, 1))]
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
                        PopupLayout = [[sg.T('This will delete all saved data for PsychoPass. Are you sure you want to continue?')],[sg.B('Yes'), sg.B('No')]]
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
                    window.close()
                    PsychoPass.Options()
            if event == 'Back':
                window.close()
                PsychoPass.Options()
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
    def ImportTMD():
        layout = [
            [sg.Image(logo)],
            [sg.Text('Please select Passwords and Key files.')],
            [sg.Text('Passwords'), sg.Input(key='-PASSWORDINPUT-'), sg.FileBrowse(file_types=[('PsychoPass File', '*.pyp')])],
            [sg.Text('Key'), sg.Input(key='-KEYINPUT-'), sg.FileBrowse(file_types=[('PsychoPass File', '*.pyp')])],
            [sg.Button('Import'), sg.Button('Back')]
            ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Import':
                PasswordInput = values['-PASSWORDINPUT-']
                KeyInput = values['-KEYINPUT-']
                TMD.Import(PasswordInput, KeyInput)
                sg.popup('Successfully Imported!')
            if event == 'Back':
                window.close()
                PsychoPass.Options()
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
    def ExportTMD(type=1):
        layout = [
            [sg.Image(logo)],
            [sg.Text('Please Select an Output Path.', font=('Helvetica', 15), size=(25, 1))],
            [sg.Text('Output Path:', font=('Helvetica'), size=(10, 1)), sg.Input(key='-OUTPATH-', size=(30, 1)), sg.SaveAs(file_types=[('PsychoPass File', '*pyp')], initial_folder=f'C:/users/{user}')],
            [sg.Button('Export Data', size=(15, 1)), sg.Button('Back', size=(15, 1))]
            ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Export Data':
                Path = values['-OUTPATH-']
                if type == 1:
                    TMD.Export(tmd2, Path)
                    window.close()
                    PsychoPass.Options()
                if type == 2:
                    TMD.Export(tmd3, Path)
                    window.close()
                    PsychoPass.Options()
            if event == 'Back':
                window.close()
                PsychoPass.Options()
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
    def Options():
        ThemeOptions = ['Default', 'LightGreen', 'LightBlue', 'LightBrown', 'LightGrey', 'LightPurple', 'DarkBlue', 'DarkBrown', 'DarkGrey', 'DarkPurple', 'Black',]
        layout = [
            [sg.Text('Options', font=('Helvetica', 20))],
            [sg.Combo(ThemeOptions, default_value=Theme, key='-THEME-', size=(20, 1)), sg.Button('Set Theme')],
            [sg.Button('Reset Login', size=(15, 1), font=('Helvetica')), sg.Button('Reset Data', size=(15, 1), font=('Helvetica')), sg.Button('Back', size=(15, 1), font=('Helvetica'))],
            [sg.Button('Import Passwords', size=(15, 1), font=('Helvetica')), sg.Button('Export Passwords', size=(15, 1), font=('Helvetica')), sg.Button('Export Key', size=(15, 1), font=('Helvetica'))]\
        ]

        window = sg.Window('Options', layout, icon=icon, element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style)
        
        while True:
            event, values = window.read()
            if event == 'Reset Login':
                window.close()
                PsychoPass.Authenticate(type=2)
            if event == 'Reset Data':
                window.close()
                PsychoPass.Authenticate(type=1)
            if event == 'Import Passwords':
                window.close()
                PsychoPass.Authenticate(type=5)
            if event == 'Export Key':
                window.close()
                PsychoPass.Authenticate(type=4)
            if event == 'Export Passwords':
                window.close()
                PsychoPass.Authenticate(type=3)
            if event == 'Set Theme':
                Json.Edit('Theme', values['-THEME-'])
                sg.theme(values['-THEME-'])
                sg.popup('Theme Applied!')
                window.close()
                PsychoPass.Options()
            if event == 'Back':
                window.close()
                PsychoPass.MainMenu()
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()

    def GeneratePassword():
        Password = Cryptography.GeneratePassword(MAX_LEN=12)
        layout = [
            [sg.Text('Your generated password is', font=('Helvetica', 16))],
            [sg.Text(Password, key='-PASSWORD-', font=('Helvetica', 16), justification='center')],
            [sg.Text('If you want to change your password, press "Regenerate" below.', font=('Helvetica', 12))],
            [sg.Text('Please enter information associated with the password below.', font=('Helvetica', 12))],
            [sg.Text('Username', size=(10, 1)), sg.Input(key='-USERNAME-', size=(20, 1))],
            [sg.Text('Email', size=(10, 1)), sg.Input(key='-EMAIL-', size=(20, 1))],
            [sg.Text('Website', size=(10, 1)), sg.Input(key='-WEBSITE-', size=(20, 1))],
            [sg.Text('Password Length', size=(14, 1))],
            [sg.Slider(range=(8, 20), default_value=12, size=(20, 12), orientation='h', key='-LENGTH_SLIDER-', relief='groove')],
            [sg.Button('Save', size=(10, 1)), sg.Button('Regenerate', size=(10, 1)), sg.Button('Back', size=(10, 1))]
        ]

        window = sg.Window('Generated Password', layout, icon=icon, element_justification='center', margins=(10, 10), use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Regenerate':
                max_len = int(values['-LENGTH_SLIDER-'])
                Password = Cryptography.GeneratePassword(MAX_LEN=max_len)
                window['-PASSWORD-'].update(Password)
            if event == 'Save':
                username = values['-USERNAME-']
                email = values['-EMAIL-']
                website = values['-WEBSITE-']
                Data = f"\n\tUsername:  {username}\n\tEmail:          {email}\n\tPassword:   {Password}\n\tWebsite:      {website}"
                Data = Cryptography.Encrypt(Data)
                TMD.Write(tmd2, Data.decode() + '\n', open_type='a')
                window['-USERNAME-'].update('')
                window['-EMAIL-'].update('')
                window['-WEBSITE-'].update('')
                sg.popup('Password saved successfully!', icon=icon, title='PsychoPass')
            if event == 'Back':
                window.close()
                PsychoPass.MainMenu()
            elif event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
    def SavePasswords():
        layout = [
            [sg.Image(logo)],
            [sg.Text("Save Passwords Here", font=('Helvetica', 16), justification='center')],
            [sg.Text('Username', size=(12, 1)), sg.Input(key='-USERNAME-', size=(40, 1))],
            [sg.Text('Email', size=(12, 1)), sg.Input(key='-EMAIL-', size=(40, 1))],
            [sg.Text('Password', size=(12, 1)), sg.Input(key='-PASSWORD-', size=(40, 1))],
            [sg.Text('Website', size=(12, 1)), sg.Input(key='-WEBSITE-', size=(40, 1))],
            [sg.Button('Save', size=(10, 1)), sg.Button('Generate', size=(10, 1)), sg.Button('Back', size=(10, 1))]
        ]

        window = sg.Window('Save Passwords', layout, icon=icon, element_justification='center', margins=(10, 10), use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Generate':
                window.close()
                PsychoPass.GeneratePassword()
            if event == 'Back':
                window.close()
                PsychoPass.MainMenu()
            if event == sg.WIN_CLOSED:
                sys.exit()
            if event == 'Save':
                username = values['-USERNAME-']
                email = values['-EMAIL-']
                password = values['-PASSWORD-']
                website = values['-WEBSITE-']
                Data = f"\n\tUsername:  {username}\n\tEmail:          {email}\n\tPassword:   {password}\n\tWebsite:      {website}"
                Data = Cryptography.Encrypt(Data)
                TMD.Write(tmd2, Data.decode() + '\n', open_type='a')
                sg.popup('Passwords saved successfully!', icon=icon, title='PsychoPass')
                window['-USERNAME-'].update('')
                window['-EMAIL-'].update('')
                window['-PASSWORD-'].update('')
                window['-WEBSITE-'].update('')
        window.close()
    def MainMenu():
        if os.path.getsize(tmd2) == 0:
            Data = ''
        if os.path.getsize(tmd2) > 0:
            try:
                Data = TMD.Read(tmd2, all_lines=True)
            except Exception as e:
                Data = 'Error loading passwords: ' + str(e)
        layout = [
            [sg.Image(logo)],
            [sg.Text('PyschoPass Menu', font=('Helvetica', 16, 'bold'))],
            [sg.Multiline(Data, size=(55, 30), key='-MULTILINE-', disabled=False, autoscroll=True, font=('Helvetica', 12))],
            [sg.Button('Save Passwords', size=(15, 1)), sg.Button('Options', size=(15, 1)), sg.Button('Clear Passwords', size=(15, 1)), sg.Button('Close', size=(15, 1))]
        ]
        window = sg.Window('PsychoPass', layout, icon=icon, margins=(20, 20), use_ttk_buttons=True, ttk_theme=ttk_style, finalize=True)
        while True:
            event, values = window.read()
            if event == 'Options':
                window.close()
                PsychoPass.Options()
            if event == 'Save Passwords':
                window.hide()
                PsychoPass.SavePasswords()
                window['-MULTILINE-'].update(Data)
                window.un_hide()
            if event == 'Clear Passwords':
                sg.popup(TMD.Clear(tmd2), icon=icon, title='PsychoPass')
                Data = ''
                window['-MULTILINE-'].update(Data)
            if event == sg.WIN_CLOSED or event == 'Close':
                sys.exit()
        window.close()
    def CreateAccount(type=1):
        layout = [
            [sg.Text('PsychoPass Login Creation', size=(24, 1), font=('Helvetica', 20), justification='center')],
            [sg.Text('Username:', size=(12, 1), font=('Helvetica', 12)), sg.Input(key='-USERNAME-', size=(20, 1), font=('Helvetica', 12))],
            [sg.Text('Password:', size=(12, 1), font=('Helvetica', 12)), sg.Input(key='-PASSWORD-', size=(20, 1), font=('Helvetica', 12), password_char='*')],
            [sg.Button('Create Account', size=(15, 1), font=('Helvetica', 12)), sg.Button('Back', size=(15, 1), font=('Helvetica', 12))]
        ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', margins=(20, 20), use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Create Account':
                Credentials = values['-USERNAME-'] + values['-PASSWORD-']
                Credentials = Cryptography.Encrypt(Credentials)
                if type == 1:
                    TMD.Write(tmd1, Credentials.decode(), open_type='w')
                    sg.popup('Account Created!', icon=icon, title='PsychoPass')
                    window.close()
                    PsychoPass.Login(Theme)
                if type == 2:
                    TMD.Clear(tmd1)
                    TMD.Write(tmd1, Credentials.decode(), open_type='w')
                    sg.popup('Account Credentials Changed!', icon=icon, title='PsychoPass')
                    window.close()
                    PsychoPass.Login(Theme)
            if event == 'Back':
                if type == 1:
                    window.close()
                    PsychoPass.Login(Theme)
                if type == 2:
                    window.close()
                    PsychoPass.Options()
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
    def Login(theme):
        sg.theme(theme)
        layout = [
            [sg.Im(logo)],
            [sg.Text('PsychoPass Login', size=(20, 1), font=('Helvetica', 20), justification='center')],
            [sg.Text('Username:', size=(12, 1), font=('Helvetica', 12)), sg.Input(key='-USERNAME-', size=(20, 1), font=('Helvetica', 12))],
            [sg.Text('Password:', size=(12, 1), font=('Helvetica', 12)), sg.Input(key='-PASSWORD-', size=(20, 1), font=('Helvetica', 12), password_char='*')],
            [sg.Button('Login', size=(15, 1), font=('Helvetica', 12)), sg.Button('Create Account', size=(15, 1), font=('Helvetica', 12))]
        ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', margins=(20, 20), use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Login':
                if os.path.getsize(tmd1) == 0:
                    sg.popup('Please Create Account.', icon=icon, title='PsychoPass')
                if os.path.getsize(tmd1) > 0:
                    Credentials = values['-USERNAME-'] + values['-PASSWORD-']
                    CheckLogin = Authentication.AuthenticateLogin(Credentials)
                    if CheckLogin is True:
                        window.close()
                        PsychoPass.MainMenu()
                    if CheckLogin is False:
                        sg.popup('Invalid Credentials', icon=icon, title='PsychoPass')
            if event == 'Create Account':
                if os.path.getsize(tmd1) == 0:
                    window.close()
                    PsychoPass.CreateAccount()
                if os.path.getsize(tmd1) > 0:
                    sg.popup('Account Already Created.', icon=icon, title='PsychoPass')
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()

try:
    Json.PreLaunch()
    TMD.Check()
    PsychoPass.Login(Theme)
except Exception as e:
    sg.PopupScrolled('Error: \n' + str(e))