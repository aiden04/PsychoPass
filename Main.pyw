import json
import os
import random
import string
import getpass
import shutil
import sys
import pyotp
import qrcode
import datetime
import PySimpleGUI as sg
import requests
import subprocess
from cryptography.fernet import Fernet
from password_strength import PasswordStats
appdata_path = os.path.join(os.environ['LOCALAPPDATA'], 'PsychoPass')
os.makedirs(appdata_path, exist_ok=True)
script_path = os.path.abspath(sys.argv[0])
CurrentDate = datetime.date.today()
root = os.path.dirname(script_path)
user = getpass.getuser()
RepoOwner = 'aiden04'
RepoName = 'PsychoPass'
CurrentVersion = f'{appdata_path}/CurrentVersion.txt'
icon = f'{root}/icon.ico'
logo = f'{root}/logo.png'
JsonPath = f'{appdata_path}/settings.json'
tmd1 = f'{appdata_path}/TMD1.pyp'
tmd2 = f'{appdata_path}/TMD2.pyp'
tmd3 = f'{appdata_path}/TMD3.pyp'
ttk_style = 'clam'
class Json:
    def PreLaunch():
        AutoLogin = Cryptography.Encrypt('False')
        JsonDefault = {
            'Theme': 'SystemDefault',
            'CreationDate': str(CurrentDate),
            'Auth': '',
            'AutoLogin': AutoLogin.decode()
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
    def DateCheck():
        CreationDate = Json.Read('CreationDate')
        if CreationDate is None:
            sg.popup("Creation Date is not available.", icon=icon, title='PsychoPass')
            return
        try:
            CreationDate = datetime.datetime.strptime(CreationDate, "%Y-%m-%d").date()
        except ValueError:
            sg.popup("Invalid date format for Creation Date.", icon=icon, title='PsychoPass')
            return
        TargetDate = CreationDate + datetime.timedelta(days=30)
        CurrentDate = datetime.date.today()
        
        if CurrentDate >= TargetDate:
            sg.popup("Password hasn't been changed in the past 30 days. Please change the password.", icon=icon, title='PsychoPass')
        else:
            pass
    def AutoLogin(check=False, edit=False, enabled=False):
        if check is True:
            Data = Json.Read('AutoLogin')
            Data = Cryptography.Decrypt(Data)
            return Data
        if edit is True:
            if enabled is True:
                Data = Cryptography.Encrypt('True')
                Json.Edit('AutoLogin', Data.decode())
                return 'Enabled'
            if enabled is False:
                Data = Cryptography.Encrypt('False')
                Json.Edit('AutoLogin', Data.decode())
                return 'Disabled'
if os.path.exists(JsonPath):
    Theme = Json.Read('Theme')
else:
    Theme = 'SystemDefault'
sg.theme(Theme)
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
        try:
            fern = Fernet(Key)
            data = fern.decrypt(Input)
            return data
        except Exception as e:
            sg.popup('Error', + str(e), icon=icon, title='PsychoPass')
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
                sg.popup('Error:' + str(e), icon=icon, title='PsychoPass')
    def Import(file_path, key_path):
        try:
            with open(file_path) as l:
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
                sg.popup('Successfully Imported', icon=icon, title='PyschoPass')
        except Exception as e:
            sg.popup('Error: ' + str(e), icon=icon, title='PsychoPass')
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
            sg.popup('Passwords saved successfully!', icon=icon, title='PsychoPass')
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
                sg.popup('Passwords Cleared', icon=icon, title='PsychoPass')
        except FileNotFoundError:
            sg.popup('TMD File not found.', icon=icon, title='PsychoPass')
    def Export(tmd, OutPath):
        try:
            shutil.copy(tmd, OutPath)
            sg.popup('Data Successfully Exported!', icon=icon, title='PsychoPass')
        except Exception as e:
            sg.popup('Error: ' + str(e), icon=icon, title='PsychoPass')
    def FactoryReset():
        try:
            os.remove(tmd1)
            os.remove(tmd2)
            os.remove(tmd3)
            os.remove(JsonPath)
            if os.path.exists(f'{appdata_path}/qrcode.png'):
                os.remove(f'{appdata_path}/qrcode.png')
            if not os.path.exists(f'{appdata_path}/qrcode.png'):
                pass
            sg.popup('All data has been reset. PsychoPass will now close.', icon=icon, title='PsychoPass')
            sys.exit()
        except Exception as e:
            sg.popup('Error: ' + str(e), icon=icon, title='PsychoPass')
class Authentication:
    def get_strength_label(strength):
        if strength < 0.25:
            return 'Weak'
        elif strength < 0.5:
            return 'Moderate'
        elif strength < 0.75:
            return 'Strong'
        else:
            return 'Very Strong'
    def AuthKey(type='Save', Key=''):
        try:
            if type == 'Save':
                Data = Cryptography.Encrypt(Key)
                Json.Edit('Auth', Data.decode())
            if type == 'Read':
                Data = Json.Read('Auth')
                key = Cryptography.Decrypt(Data)
                return key
        except Exception as e:
            sg.popup('Error: ', + str(e), icon=icon, title='PsychoPass')
    def CheckQR(key):
        try:
            SavedKey = Authentication.AuthKey(type='Read')
            totp = pyotp.TOTP(SavedKey)
            generated_code = totp.now()
            if generated_code == key:
                return True
            else:
                return False
        except Exception as e:
            sg.popup('Error: ', + str(e), icon=icon, title='PsychoPass')
    def CreateQR():
        try:
            SecretKey = pyotp.random_base32()
            KeyPath = Authentication.AuthKey(type='Save', Key=SecretKey)
            totp = pyotp.TOTP(SecretKey)
            ProvisioningURI = totp.provisioning_uri(name='PsychoPass', issuer_name='')
            QRCode = qrcode.make(ProvisioningURI)
            QRCodeName = f'{appdata_path}/qrcode.png'
            QRCode.save(QRCodeName)
            return QRCodeName
        except Exception as e:
            sg.popup('Error: ' + str(e), icon=icon, title='PsychoPass') 
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
class PsychoPass:
    def CheckVer():
        if not os.path.exists(CurrentVersion):
            with open(CurrentVersion, 'w') as f:
                f.write('1.3.1')
                f.close()
        if os.path.exists(CurrentVersion):
            pass
    def CheckForUpdate():
        try:
            url = f"https://api.github.com/repos/{RepoOwner}/{RepoName}/releases/latest"
            response = requests.get(url)
            release = response.json()
            LatestVersion = release['tag_name']
            downloadUrl = release['assets'][0]['browser_download_url']
            return LatestVersion, downloadUrl
        except requests.exceptions.RequestException:
            return None, None
    def Update(download_url, Version):
        try:
            with open(CurrentVersion, 'w') as f:
                f.truncate(0)
                f.write(Version)
            response = requests.get(download_url)
            with open(f'{appdata_path}/update.exe', 'wb') as file:
                file.write(response.content)            
            layout0 = [[sg.T('Successfully Downloaded Update! Install Now?')], [sg.B('Yes'), sg.B('No')]]
            window0 = sg.Window('PsychoPass', layout0, icon=icon, element_justification='center', margins=(10, 10), use_ttk_buttons=True, ttk_theme=ttk_style)
            event0, _ = window0.read()
            if event0 == 'Yes':
                window0.hide()
                with open(f'{appdata_path}/update.bat', 'w') as file:
                    file.write(f'start "" "{appdata_path}/update.exe"\n')
                    file.write('exit\n')
                window0.close()
                sg.popup('Program will be closed for update.', icon=icon, title='PsychoPass')
                sg.popup_auto_close('Installing update...', auto_close_duration=3000, non_blocking=True)
                subprocess.Popen(f'{appdata_path}/update.bat', shell=True)
                sys.exit()
            if event0 == 'No':
                window0.close()
                PsychoPass.Options()               
            if event0 == sg.WIN_CLOSED:
                sys.exit()       
        except requests.exceptions.RequestException as e:
            sg.popup(f'error: {e}')
    def Authenticate(type=1):
        layout = [
            [sg.Image(logo)],
            [sg.Text('Please Verify Credentials.', font=('Helvetica', 20), size=(20, 1))],
            [sg.Text('Username:', size=(10, 1)), sg.Input(key='-USERNAME-', size=(20, 1))],
            [sg.Text('Password:', size=(10, 1)), sg.Input(key='-PASSWORD-', size=(20, 1), password_char='*')],
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
                    if type == 6:
                        window.close()
                        PsychoPass.TwoFactorAuth()
                if CheckLogin is False:
                    sg.popup('Invalid Credentials.', icon=icon, title='PsychoPass')
                    window.close()
                    PsychoPass.Options()
            if event == 'Back':
                window.close()
                PsychoPass.Options()
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
    def TwoFactorAuth():
        QRCode = Authentication.CreateQR()
        layout = [
            [sg.Image(logo)],
            [sg.Text('Scan this QR Code in an Authenticator App', font=('Helvetica'))],
            [sg.Image(QRCode, key='-QR-')],
            [sg.Button('Regenerate', size=(10,1)), sg.Button('Back', size=(10,1))]
            ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', element_padding=10, use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Regenerate':
                QRCode = Authentication.CreateQR()
                window['-QR-'].update(QRCode)
            if event == 'Back':
                window.close()
                PsychoPass.Options()
            if event == sg.WIN_CLOSED:
                sys.exit()
    def ImportTMD():
        layout = [
            [sg.Image(logo)],
            [sg.Text('Please select Passwords and Key files.', font=('Helvetica'), size=(30, 1))],
            [sg.Text('Passwords', size=(10, 1)), sg.Input(key='-PASSWORDINPUT-', size=(30, 1)), sg.FileBrowse(file_types=[('PsychoPass File', '*.pyp')])],
            [sg.Text('Key', size=(10, 1)), sg.Input(key='-KEYINPUT-', size=(30, 1)), sg.FileBrowse(file_types=[('PsychoPass File', '*.pyp')])],
            [sg.Button('Import', size=(10, 1)), sg.Button('Back', size=(10, 1))]
            ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Import':
                PasswordInput = values['-PASSWORDINPUT-']
                KeyInput = values['-KEYINPUT-']
                TMD.Import(PasswordInput, KeyInput)
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
            [sg.Text('Output Path:', size=(10, 1)), sg.Input(key='-OUTPATH-', size=(30, 1)), sg.SaveAs(file_types=[('PsychoPass File', '*pyp')], initial_folder=f'C:/users/{user}')],
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
        ThemeOptions = ['Default', 'LightGreen', 'LightBlue', 'LightBrown', 'LightGrey', 'LightPurple', 'DarkBlue', 'DarkBrown', 'DarkGrey', 'DarkPurple', 'Black']
        AutoLogin = Json.AutoLogin(check=True)
        if os.path.exists(JsonPath):
            Theme = Json.Read('Theme')
        else:
            Theme = 'SystemDefault'
        Data = 'Enable AutoLogin'
        if AutoLogin == 'False':
            Data = 'Enable AutoLogin'
        if AutoLogin == 'True':
            Data = 'Disable AutoLogin'
        layout = [
            [sg.Text('Options', font=('Helvetica', 20))],
            [sg.Combo(ThemeOptions, default_value=Theme, key='-THEME-', size=(20, 1)), sg.Button('Set Theme')],
            [sg.Button('Reset Login', size=(15, 1), font=('Helvetica')), sg.Button('Reset Data', size=(15, 1), font=('Helvetica')), sg.Button('Back', size=(15, 1), font=('Helvetica'))],
            [sg.Button('Import Passwords', size=(15, 1), font=('Helvetica')), sg.Button('Export Passwords', size=(15, 1), font=('Helvetica')), sg.Button('Export Key', size=(15, 1), font=('Helvetica'))],
            [sg.Button(Data, size=(15, 1), font=('Helvetica'), key='-AUTOLOGIN-', ), sg.Button('Enable 2FA', size=(15, 1), font=('Helvetica')), sg.Button('Check for Update', size=(15, 1), font=('Helvetica'))]
        ]
        window = sg.Window('Options', layout, icon=icon, element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            AutoLogin = Json.AutoLogin(check=True)
            if event == 'Check for Update':
                window.close()
                LatestVersion, DownloadURL = PsychoPass.CheckForUpdate()
                with open(CurrentVersion) as file:
                    Version = file.read()
                if LatestVersion > Version:
                    ConfirmLayout = [
                        [sg.Image(logo)],
                        [sg.Text('Update Avalible, would you like to download the update?', font=('Helvetica', 15))],
                        [sg.Button('Yes', size=(10, 1)), sg.Button('No', size=(10, 1))]
                        ]
                    ConfirmWindow = sg.Window('PsychoPass', ConfirmLayout, icon=icon, element_justification='center', margins=(10, 10), use_ttk_buttons=True, ttk_theme=ttk_style)
                    confirm_event, _ = ConfirmWindow.read()
                    if confirm_event == 'Yes':
                        ConfirmWindow.close()
                        PsychoPass.Update(DownloadURL, LatestVersion)
                    if confirm_event == 'No':
                        ConfirmWindow.close()
                        PsychoPass.Options()
                    if confirm_event == sg.WIN_CLOSED:
                        sys.exit()
                else:
                    sg.popup('PsychoPass is already running the latest version', icon=icon)
                    PsychoPass.Options()
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
                sg.popup('Theme Applied!', icon=icon, title='PsychoPass')
                window.close()
                PsychoPass.Options()
            if event == 'Back':
                window.close()
                PsychoPass.MainMenu()
            if event == 'Enable 2FA':
                window.close()
                PsychoPass.Authenticate(type=6)
            if event == '-AUTOLOGIN-':
                if AutoLogin == 'False':
                    Json.AutoLogin(check=False, edit=True, enabled=True)
                    SendBack = 'Disable AutoLogin'
                    sg.popup('Auto Login Enabled', icon=icon, title='PsychoPass')
                    window['-AUTOLOGIN-'].update(SendBack)
                if AutoLogin == 'True':
                    Json.AutoLogin(check=False, edit=True, enabled=False)
                    SendBack = 'Enable AutoLogin'
                    sg.popup('Auto Login Disabled', icon=icon, title='PsychoPass')
                    window['-AUTOLOGIN-'].update(SendBack)
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
            [sg.Checkbox('', default=True, key='-USERSELECT-'), sg.Text('Username', size=(10, 1)), sg.Input(key='-USERNAME-', size=(20, 1))],
            [sg.Checkbox('', default=True, key='-EMAILSELECT-'), sg.Text('Email', size=(10, 1)), sg.Input(key='-EMAIL-', size=(20, 1))],
            [sg.Checkbox('', default=True, key='-WEBSELECT-'), sg.Text('Website', size=(10, 1)), sg.Input(key='-WEBSITE-', size=(20, 1))],
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
                username = values['-USERNAME-'] if values['-USERSELECT-'] else ''
                email = values['-EMAIL-'] if values['-EMAILSELECT-'] else ''
                website = values['-WEBSITE-'] if values['-WEBSELECT-'] else ''
                data = ''
                if username:
                    data += f"\n\tUsername:   {username}"
                if email:
                    data += f"\n\tEmail:          {email}"
                data +=f"\n\tPassword:          {Password}"
                if website:
                    data += f"\n\tWebsite:      {website}"
                data = Cryptography.Encrypt(data)
                TMD.Write(tmd2, data.decode() + '\n', open_type='a')
                window['-USERNAME-'].update('')
                window['-EMAIL-'].update('')
                window['-WEBSITE-'].update('')
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
            [sg.Checkbox('', default=True, key='-USERSELECT-'), sg.Text('Username', size=(12, 1)), sg.Input(key='-USERNAME-', size=(40, 1))],
            [sg.Checkbox('', default=True, key='-EMAILSELECT-'), sg.Text('Email', size=(12, 1)), sg.Input(key='-EMAIL-', size=(40, 1))],
            [sg.Checkbox('', default=True, key='-PASSSELECT-'), sg.Text('Password', size=(12, 1)), sg.Input(key='-PASSWORD-', size=(40, 1), enable_events=True)],
            [sg.Checkbox('', default=True, key='-WEBSELECT-'), sg.Text('Website', size=(12, 1)), sg.Input(key='-WEBSITE-', size=(40, 1))],
            [sg.Text('Password Strength:', size=(15, 1)), sg.Text('', size=(20, 1), key='-STRENGTH-')],
            [sg.Button('Save', size=(10, 1)), sg.Button('Generate', size=(10, 1)), sg.Button('Back', size=(10, 1))]
        ]
        window = sg.Window('Save Passwords', layout, icon=icon, element_justification='center', margins=(10, 10), use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == '-PASSWORD-':
                password = values['-PASSWORD-']
                if password:
                    password_stats = PasswordStats(password)
                    strength = password_stats.strength()
                else:
                    strength = 0
                strength_label = Authentication.get_strength_label(strength)
                window['-STRENGTH-'].update(strength_label)
            if event == 'Generate':
                window.close()
                PsychoPass.GeneratePassword()
            if event == 'Back':
                window.close()
                PsychoPass.MainMenu()
            if event == sg.WINDOW_CLOSED:
                sys.exit()
            if event == 'Save':
                username = values['-USERNAME-'] if values['-USERSELECT-'] else ''
                email = values['-EMAIL-'] if values['-EMAILSELECT-'] else ''
                password = values['-PASSWORD-'] if values['-PASSSELECT-'] else ''
                website = values['-WEBSITE-'] if values['-WEBSELECT-'] else ''
                data = ''
                if username:
                    data += f"\n\tUsername:   {username}"
                if email:
                    data += f"\n\tEmail:          {email}"
                if password:
                    data += f"\n\tPassword:   {password}"
                if website:
                    data += f"\n\tWebsite:      {website}"
                data = Cryptography.Encrypt(data)
                TMD.Write(tmd2, data.decode() + '\n', open_type='a')
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
            [sg.Multiline(Data, size=(55, 30), key='-MULTILINE-', disabled=True, autoscroll=False, font=('Helvetica', 12))],
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
                TMD.Clear(tmd2)
                Data = ''
                window['-MULTILINE-'].update(Data)
            if event == sg.WIN_CLOSED or event == 'Close':
                sys.exit()
        window.close()
    def CreateAccount(type=1):
        layout = [
            [sg.Text('PsychoPass Login Creation', size=(24, 1), font=('Helvetica', 20), justification='center')],
            [sg.Text('Username:', size=(12, 1), font=('Helvetica', 12)), sg.Input(key='-USERNAME-', size=(20, 1), font=('Helvetica', 12))],
            [sg.Text('Password:', size=(12, 1), font=('Helvetica', 12)), sg.Input(key='-PASSWORD-', size=(20, 1), font=('Helvetica', 12), password_char='*', enable_events=True)],
            [sg.Text('Password Strength:', size=(15, 1)), sg.Text('', size=(20, 1), key='-STRENGTH-')],
            [sg.Button('Create Account', size=(15, 1), font=('Helvetica', 12)), sg.Button('Back', size=(15, 1), font=('Helvetica', 12))]
        ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', margins=(20, 20), use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == '-PASSWORD-':
                password = values['-PASSWORD-']
                if password:
                    password_stats = PasswordStats(password)
                    strength = password_stats.strength()
                else:
                    strength = 0
                strength_label = Authentication.get_strength_label(strength)
                window['-STRENGTH-'].update(strength_label)
            if event == 'Create Account':
                Credentials = values['-USERNAME-'] + values['-PASSWORD-']
                Credentials = Cryptography.Encrypt(Credentials)
                Json.Edit('CreationDate', str(CurrentDate))
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
    def ForgotPassword():
        layout = [
            [sg.Image(logo)],
            [sg.Text('Please enter the code provided by your Authentication App below:', font=('Helvetica'))],
            [sg.Text('Pin', size=(4,1)), sg.Input(key='-KEY-')],
            [sg.Button('Reset Password', size=(14,1)), sg.Button('Back', size=(14,1))]
            ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', margins=(20, 20), use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Reset Password':
                Auth = Authentication.CheckQR(values['-KEY-'])
                if Auth is True:
                    window.close()
                    PsychoPass.CreateAccount(type=2)
                else:
                    sg.popup('Incorrect Code.', icon=icon, title='PsychoPass')
            if event == 'Back':
                window.close()
                PsychoPass.Login(Theme)
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
            [sg.Button('Login', size=(15, 1), font=('Helvetica', 12)), sg.Button('Create Account', size=(15, 1), font=('Helvetica', 12)), sg.Button('Forgot Password', size=(15, 1), font=('Helvetica', 12))]
        ]
        window = sg.Window('PsychoPass', layout, icon=icon, element_justification='center', margins=(20, 20), use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            if event == 'Forgot Password':
                if os.path.exists(f'{appdata_path}/qrcode.png'):
                    window.close()
                    PsychoPass.ForgotPassword()
                else:
                    sg.popup('2 Factor Authentication not enabled.', icon=icon, title='PsychoPass')
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
                    PsychoPass.CreateAccount(type=1)
                if os.path.getsize(tmd1) > 0:
                    sg.popup('Account Already Created.', icon=icon, title='PsychoPass')
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
TMD.Check()
Json.PreLaunch()
Json.DateCheck()
PsychoPass.CheckVer()
AutoLogin = Json.AutoLogin(check=True)
if AutoLogin == 'True':
    try:
        PsychoPass.MainMenu()
    except Exception as e:
        print('Error: ' + str(e))
        sg.PopupScrolled('Error: \n' + str(e), icon=icon, title='PsychoPass')
if AutoLogin == 'False':
    try:
        PsychoPass.Login(Theme)
    except Exception as e:
        print('Error: ' + str(e))
        sg.PopupScrolled('Error: \n' + str(e), icon=icon, title='PsychoPass')
