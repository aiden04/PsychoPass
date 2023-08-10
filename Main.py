import sqlite3
import PySimpleGUI as sg
from cryptography.fernet import Fernet
import pyotp
import qrcode
import os
import sys
import datetime
import json
import requests
import subprocess
import string
import random

appdata_path = os.path.join(os.environ['LOCALAPPDATA'], 'PsychoPass')
os.makedirs(appdata_path, exist_ok=True)
CurrentDate = datetime.date.today()
root = os.path.dirname(sys.argv[0])
JsonPath = f'{appdata_path}/settings.json'
icon = f'{root}/assets/icon.ico'
logo = f'{root}/assets/logo.png'
ttk_style = 'clam'

class QR:
    def AuthKey(type='Save', Key=''):
        cryptokey = DataBaseMG.get_table_value('Auth', 'Key')
        try:
            if type == 'Save':
                Data = Cryptography.encrypt(Key, cryptokey)
                Json.Edit('Auth', Data.decode())
            if type == 'Read':
                Data = Json.Read('Auth')
                key = Cryptography.decrypt(Data, cryptokey)
                return key
        except Exception as e:
            sg.popup('Error: ' + str(e), icon=icon, title='PsychoPass')
    def CreateQR():
        try:
            SecretKey = pyotp.random_base32()
            totp = pyotp.TOTP(SecretKey)
            ProvisioningURI = totp.provisioning_uri(name='PsychoPass', issuer_name='')
            QRCode = qrcode.make(ProvisioningURI)
            QRCodeName = f'{appdata_path}/qrcode.png'
            QRCode.save(QRCodeName)
            return QRCodeName
        except Exception as e:
            sg.popup('Error: ' + str(e), icon=icon, title='PsychoPass') 
    def CheckQR(key):
        try:
            print(f'Key: {key}')
            SavedKey = QR.AuthKey(type='Read')
            print(f"Saved Key: {SavedKey}")
            totp = pyotp.TOTP(SavedKey)
            print(f'Totp: {totp}')
            generated_code = totp.now()
            print(f'Generated Code: {generated_code}')
            if generated_code == key:
                return True
            else:
                return False
        except Exception as e:
            sg.popup('Error: ' + str(e), icon=icon, title='PsychoPass')
class Json:
    def PreLaunch():
        key = DataBaseMG.get_table_value("Auth", "Key")
        AutoLogin = Cryptography.encrypt('False', key)
        JsonDefault = {
            'Theme': 'SystemDefault',
            'CreationDate': str(CurrentDate),
            'Auth': '',
            'AutoLogin': AutoLogin.decode(),
            'Current Version': '1.3.1'
        }
        if os.path.exists(JsonPath):
            return
        if not os.path.exists(JsonPath):
            print(f'Create Settings file at {os.path.exists(JsonPath)}')
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
            pass
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
        key = DataBaseMG.get_table_value("Auth", "Key")
        if check is True:
            Data = Json.Read('AutoLogin')
            Data = Cryptography.decrypt(Data, key).decode()
            return Data
        if edit is True:
            if enabled is True:
                Data = Cryptography.encrypt('True', key)
                print('Changing AutoLogin to False')
                Json.Edit('AutoLogin', Data.decode())
                return 'Enabled'
            if enabled is False:
                Data = Cryptography.encrypt('False', key)
                print('Changing AutoLogin to True')
                Json.Edit('AutoLogin', Data.decode())
                return 'Disabled'
if os.path.exists(JsonPath):
    Theme = Json.Read('Theme')
else:
    Theme = 'SystemDefault'
sg.theme(Theme)
class DataBaseMG:
    def init():
        DataBase = sqlite3.connect(f"{root}/PsychoPassDB.db")
        cur = DataBase.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS Auth (Username TEXT, Password TEXT, Key TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Cell0 (Cell TEXT)''')
        DataBase.commit()
        DataBase.close()
    def createauth(tuple):
        DataBase = sqlite3.connect(f"{root}/PsychoPassDB.db")
        cur = DataBase.cursor()
        print(f"recieved tuple: {tuple}")
        Json.Edit('CreationDate', str(CurrentDate))
        cur.execute("INSERT INTO Auth (Username, Password, Key) VALUES (?, ?, ?)", (tuple))
        DataBase.commit()
        DataBase.close()
        return "Account Created!"
    def is_value(table, value):
        DataBase = sqlite3.connect(f"{root}/PsychoPassDB.db")
        cur = DataBase.cursor()
        query = f"SELECT {value} FROM {table}"
        print(f"Query: {query}")
        cur.execute(query)
        result = cur.fetchone()
        DataBase.close()
        if result:
            print(f"is_value: {value} found")
            return True
        else:
            print(f"is_value: {value} not found")
            return False
    def is_table(table_name):
        DataBase = sqlite3.connect(f'{root}/PsychoPassDB.db')
        cur = DataBase.cursor()
        try:
            query = f"SELECT name FROM sqlite_master WHERE type='table' AND name={table_name}"
            print(f'Query: {query}')
            cur.execute(query)
            results = cur.fetchone()
            if results:
                print(f"is_table: {table_name} found.")
                return True
            else:
                print(f"is_table: {table_name} not found.")
                return False
        except Exception as e:
            print(f'error: {str(e)}')
    def get_table_value(table, value):
        DataBase = sqlite3.connect(f'{root}/PsychoPassDB.db')
        cur = DataBase.cursor()
        query = f"SELECT {value} FROM {table}"
        print(f'Query: {query}')
        cur.execute(query)
        result = cur.fetchone()
        DataBase.close()
        if result:
            value = result[0]
            print(f'retrievied results: {value}')
            return value
        else:
            return None
    def update_table(table, column, value):
        DataBase = sqlite3.connect(f'{root}/PsychoPassDB.db')
        cur = DataBase.cursor()
        query = f'UPDATE {table} SET {column}=?'
        print(f'Query: {query}')
        cur.execute(query, (value,))
        DataBase.commit()
        DataBase.close()
        return "Updated"
    def login(username, password):
        key = DataBaseMG.get_table_value("Auth", "Key")
        loaded_username = Cryptography.decrypt(DataBaseMG.get_table_value("Auth", "Username"), key)
        loaded_password = Cryptography.decrypt(DataBaseMG.get_table_value("Auth", "Password"), key)
        print(f"loaded username: {loaded_username.decode()}")
        print(f"loaded password: {loaded_password.decode()}")
        print(f"recieved username: {username}")
        print(f"recieved password: {password}")
        if username == loaded_username.decode() and password == loaded_password.decode():
            return True
        else:
            return False
class Cells:
    def add_cells(int):
        database_path = f"{root}/PsychoPassDB.db"
        DataBase = sqlite3.connect(database_path)
        cur = DataBase.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cur.fetchall()]   
        table_name = f"Cell{int}"
        while True:
            if table_name not in existing_tables:
                try:
                    print(f'add_cells: cell {int} is avalible!')
                    cur.execute(f"CREATE TABLE {table_name} (Username TEXT, Password TEXT, Email TEXT, Website TEXT)")
                    DataBase.commit()
                    DataBase.close()
                    print(f'add_cells: returning table_name {table_name}')
                    return table_name
                except sqlite3.Error as e:
                    print("Error:", e)
                    DataBase.close()
                    return table_name
            else:
                DataBase.close()
                cell_number = int + 1
                print(f'add_cells: {int} already exists. Trying next cell.')
                return Cells.add_cells(cell_number)

    def save_cell(username, password, email, website, key):
        encrypted_username = Cryptography.encrypt(username, key)
        encrypted_password = Cryptography.encrypt(password, key)
        encrypted_email = Cryptography.encrypt(email, key)
        encrypted_website = Cryptography.encrypt(website, key)
        cell_info = (encrypted_username.decode(), encrypted_password.decode(), encrypted_email.decode(), encrypted_website.decode())
        cell = Cells.add_cells(1)
        print(f"save_cell: saving to {cell}.")
        database_path = f"{root}/PsychoPassDB.db"
        DataBase = sqlite3.connect(database_path)
        cur = DataBase.cursor()
        query = f'INSERT INTO {cell} (Username, Password, Email, Website) VALUES (?, ?, ?, ?)'
        print(f'Query: {query}')
        cur.execute(query, cell_info)
        DataBase.commit()
        DataBase.close()
        return "Saved"
    def delete_cell(cell):
        DataBase = sqlite3.connect(f'{root}/PsychoPassDB.db')
        cur = DataBase.cursor()
        query = f'DROP TABLE IF EXISTS {cell}'
        print(f'Query: {query}')
        cur.execute(query)
        DataBase.commit()
        DataBase.close()
        print(f'delete_cell: {cell} Deleted')
        return "Deleted"
    def update_cell(cell, username, password, email, website, key):
        DataBase = sqlite3.connect(f'{root}/PsychoPassDB.db')
        cur = DataBase.cursor()
        encrypted_username = Cryptography.encrypt(username, key)
        encrypted_password = Cryptography.encrypt(password, key)
        encrypted_email = Cryptography.encrypt(email, key)
        encrypted_website = Cryptography.encrypt(website, key)
        query = f'UPDATE {cell} SET Username=?, Password=?, Email=?, Website=?'
        print(f'Update Cell Query: {query}')
        cur.execute(query, (encrypted_username, encrypted_password, encrypted_email, encrypted_website))
        DataBase.commit()
        DataBase.close()
        return "Updated"
    def export_all_cells(cell_number):
        cell_file_structure = {
            "Cell0": {
                "Username": "",
                "Password": "",
                "Email": "",
                "Website": ""
            }
        }
        print(f'export_all_cells: cell_file_structure({cell_file_structure})')
        DataBase = sqlite3.connect(f'{root}/PsychoPassDB.db')
        cur = DataBase.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Cell%'")
        cell_tables = [row[0] for row in cur.fetchall() if row[0] != 'Cell0']
        print(f'export_all_cells: {cell_tables}')
        cell_name = f'Cell{cell_number}'
        if not os.path.exists(f'{appdata_path}/temp_transfer.json'):
            with open(f'{appdata_path}/temp_transfer.json', 'w') as file:
                print(f'export_all_cells: creating temp dump at {appdata_path}/temp_transfer.json')
                json.dump(cell_file_structure, file)
                cell_data = ''
        else:
            with open(f'{appdata_path}/temp_transfer.json', 'r') as file:
                cell_data = json.load(file)
                print(f'export_all_cells: data found({cell_data})')
        
            if cell_name in cell_data:
                print(f'export_all_cells: {cell_number} is already in use! Trying next cell.')
                cell_number = cell_number + 1
                Cells.update_cell(cell_number)
            
        if cell_name not in cell_data:
            print(f'export_all_cells: {cell_number} found not in use!')
            username = DataBaseMG.get_table_value(f'{cell_name}', 'Username')
            print(username)
            password = DataBaseMG.get_table_value(f'{cell_name}', 'Password')
            email = DataBaseMG.get_table_value(f'{cell_name}', 'Email')
            website = DataBaseMG.get_table_value(f'{cell_name}', 'Website')
            print(f'export_all_cells:\nUsername: {username}\nPassword: {password}\nEmail: {email}\nWebsite: {website}')
            cell_info = {
                cell_name: {
                    "Username": username,
                    "Password": password,
                    "Email": email,
                    "Website": website
                }
            }
            print(f'export_all_cells: cell_info({cell_info})')
            with open(f'{appdata_path}/temp_transfer.json', 'w') as file:
                json.dump(cell_info, file)
            
            next_cell_number = cell_number + 1
            if next_cell_number <= len(cell_tables):
                Cells.export_all_cells(next_cell_number)
    def count_cells():
        DataBase = sqlite3.connect(f'{root}/PsychoPassDB.db')
        cur = DataBase.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Cell%'")
        cells = [row[0] for row in cur.fetchall() if row[0] != 'Cell0']
        print(f'cell_count: Cells({cells})')
        cell_count = len(cells)
        print(f'cell_count: ({cell_count}) cells counted')
        DataBase.close()
        return cell_count
    def remove_all_cells():
        DataBase = sqlite3.connect(f'{root}/PsychoPassDB.db')
        cur = DataBase.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Cell%'")
        cell_tables = [row[0] for row in cur.fetchall() if row[0] != 'Cell0']
        print(f'remove_all_cells: cell_tables({cell_tables})')
        for table in cell_tables:
            query = f"DROP TABLE IF EXISTS {table}"
            print(f'Query: {query}')
            cur.execute(query)
            print(f"Table {table} deleted.")

        DataBase.commit()
        DataBase.close()
class Cryptography:
    def gen_key():
        key = Fernet.generate_key()
        print(f"generated key: {key}")
        return key.decode()
    def encrypt(String, Key):
        cipher = Fernet(Key)
        encrypted_string = cipher.encrypt(String.encode())
        print(f"encrypt: raw:({String}), encrypted:({encrypted_string}), key:({Key})")
        return encrypted_string
    def decrypt(String, Key):
        cipher = Fernet(Key)
        decrypted_string = cipher.decrypt(String)
        print(f"decrypt: raw:({String}), decrypted:({decrypted_string}), key:({Key})")
        return decrypted_string
    def GeneratePassword(MAX_LEN=12):
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(MAX_LEN))
        return password
class Update():
    def check():
        try:
            RepoOwner = 'aiden04'
            RepoName = 'PsychoPass'
            url = f'https://api.github.com/repos/{RepoOwner}/{RepoName}/releases/latest' 
            response = requests.get(url)
            release = response.json()
            LatestVersion = release['tag_name']
            downloadUrl = release['assets'][0]['browser_download_url']
            return LatestVersion, downloadUrl
        except requests.exceptions.RequestException:
            return None, None
    def Update(downloadUrl, Version):
        try:
            Json.Edit('Current Version', Version)
            response = requests.get(downloadUrl)
            with open(f'{appdata_path}/update.exe', 'wb') as file:
                file.write(response.content)
            layout = [[sg.Image(logo)],[sg.Text('Successfully downloaded update! Would you like to update now?', font=(20))],[sg.Button('Update'), sg.Button('Cancel')]]
            window = sg.Window('PsychoPass', layout)
            event, _ = window.read()
            if event == 'Update':
                window.close()
                sg.popup('Program will be closed for update.', icon=icon, title='PsychoPass')
                sg.popup_auto_close('Installing update...', auto_close_duration=3000, non_blocking=True)
                subprocess.Popen(f'{appdata_path}/update.exe', shell=True)
                sys.exit()
            if event == 'No':
                window.close()
                PsychoPassGUI.options()
            if event == sg.WIN_CLOSED:
                sys.exit()
        except requests.exceptions.RequestException as e:
            sg.popup(f'error: {e}')
class PsychoPassGUI:
    def TwoFactorAuth():
        QRCode = QR.CreateQR()
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
                QRCode = QR.CreateQR()
                window['-QR-'].update(QRCode)
            if event == 'Back':
                window.close()
                PsychoPassGUI.options()
            if event == sg.WIN_CLOSED:
                sys.exit()
    def options():
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
            [sg.Button('Import Passwords', size=(15, 1), font=('Helvetica')), sg.Button('Export Passwords', size=(15, 1), font=('Helvetica'))],
            [sg.Button(Data, size=(15, 1), font=('Helvetica'), key='-AUTOLOGIN-', ), sg.Button('Enable 2FA', size=(15, 1), font=('Helvetica')), sg.Button('Check for Update', size=(15, 1), font=('Helvetica'))]
        ]
        window = sg.Window('Options', layout, icon=icon, element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style)
        while True:
            event, values = window.read()
            AutoLogin = Json.AutoLogin(check=True)
            if event == 'Enable 2FA':
                window.close()
                PsychoPassGUI.TwoFactorAuth()
            if event == 'Reset Data':
                window.close()
                layout = [[sg.Im(logo)],[sg.T('Are you sure you want to remove all data?', font=(20))],[sg.B('Yes'), sg.B('No')]]
                window = sg.Window('PsychoPass', layout)
                event, _ = window.read()
                if event == 'Yes':
                    subprocess.run(['cmd', '/c', 'del', f'{root}\\PsychoPassDB.db'], shell=True)
                    subprocess.run(['cmd', '/c', 'del', f'{appdata_path}\\settings.json'], shell=True)
                    sys.exit()
                if event == 'No' or event == sg.WIN_CLOSED():
                    window.close()
                    PsychoPassGUI.options()
            if event == 'Reset Login':
                window.close()
                PsychoPassGUI.createaccount(type="Change Auth")
            if event == 'Export Passwords':
                Cells.export_all_cells(1)
            if event == 'Check for Update':
                LatestVersion, downloadUrl = Update.check()
                CurrentVersion = Json.Read('Current Version')
                if CurrentVersion < LatestVersion:
                    updatelayout = [[sg.Text('Update found. Would you like to download now?')], [sg.Button('Download Update'), sg.Button('Cancel')]]
                    updatewindow = sg.Window('PsychoPass', updatelayout)
                    updateevent, _ = updatewindow.read()
                    if updateevent == 'Download Update':
                        window.close()
                        updatewindow.close()
                        Update.Update(downloadUrl, LatestVersion)
                    if updateevent == 'Cancel':
                        updatewindow.close()
                if CurrentVersion == LatestVersion or CurrentVersion > LatestVersion:
                    sg.popup('Youn are already running on the latest version!', icon=icon, title='PsychoPass')
            if event == 'Set Theme':
                Json.Edit('Theme', values['-THEME-'])
                sg.theme(values['-THEME-'])
                sg.popup('Theme Applied!', icon=icon, title='PsychoPass')
                window.close()
                PsychoPassGUI.options()
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
            if event == 'Back':
                window.close()
                PsychoPassGUI.mainmenu()
    def passwordlist():
        key = DataBaseMG.get_table_value("Auth", "Key")
        database_path = f"{root}/PsychoPassDB.db"
        DataBase = sqlite3.connect(database_path)
        cur = DataBase.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Cell%'")
        cell_tables = [row[0] for row in cur.fetchall() if row[0] != 'Cell0']
        print(f'Found Tables: {cell_tables}')
        cells_per_row = 5
        rows_per_page = 3
        current_page = 0
        max_pages = (len(cell_tables) + cells_per_row * rows_per_page - 1) // (cells_per_row * rows_per_page)
        def update_layout(page_str):
            page = int(page_str)
            rows = []
            start_idx = page * rows_per_page * cells_per_row
            end_idx = min(start_idx + rows_per_page * cells_per_row, len(cell_tables) * cells_per_row)

            for i in range(start_idx, end_idx, cells_per_row):
                row = []
                for table in cell_tables[i:i + cells_per_row]:
                    cur.execute(f"SELECT Username, Password, Email, Website FROM {table}")
                    cell_data = cur.fetchone()
                    if cell_data:
                        print(f'Cell Data: {cell_data}')
                        username, password, email, website = cell_data
                        frame_key = f'-{table}_FRAME-'
                        cell_info = (
                            f"Username: {Cryptography.decrypt(username, key).decode()}\n"
                            f"Password: {Cryptography.decrypt(password, key).decode()}\n"
                            f"Email: {Cryptography.decrypt(email, key).decode()}\n"
                            f"Website: {Cryptography.decrypt(website, key).decode()}"
                        )
                        row.append(sg.Frame(table, [
                            [sg.Text(cell_info, size=(25, 5), pad=5)],
                            [sg.Button('Delete', key=f'-{table}_DELETE-', size=8, pad=5), sg.Button('Edit', key=f'-{table}_EDIT-', size=8, pad=5)]
                        ], size=(250, 165), key=frame_key, element_justification='center', pad=5))
                rows.append(row)

            layout = [
                [sg.Image(logo)],
                [sg.Text('PsychoPass Passwords', font=(35))],
            ]
            for row in rows:
                layout.append(row)
            layout.append([sg.Text(f'Page '), sg.Input(page + 1, key='-PAGE-', size=3), sg.Text(f'/{max_pages}', key='-PAGE-NUM-'), sg.Button('Set Page')])
            layout.append([sg.Button('Previous Page'), sg.Button('Save Password'), sg.Button('Clear Passwords'), sg.Button('Back'), sg.Button('Next Page')])
            return layout
        layout = update_layout(current_page)
        window = sg.Window('PsychoPass', layout, size=(1400, 825), icon=icon, use_ttk_buttons=True, ttk_theme=ttk_style, element_padding=5, element_justification='center')
        print("Number of layout elements:", len(layout))
        while True:
            event, values = window.read()
            if event == 'Set Page':
                new_page = int(values['-PAGE-']) - 1
                if 0 <= new_page < max_pages:
                    current_page = new_page
                    layout = update_layout(current_page)
                    window.close()
                    window = sg.Window('PsychoPass', layout, size=(1400, 825), icon=icon, use_ttk_buttons=True, ttk_theme=ttk_style, element_padding=5, element_justification='center')
            if event == sg.WIN_CLOSED:
                sys.exit()
            if event == 'Previous Page' and current_page > 0:
                current_page -= 1
                layout = update_layout(current_page)
                window.close()
                window = sg.Window('PsychoPass', layout, size=(1400, 825), icon=icon, use_ttk_buttons=True, ttk_theme=ttk_style, element_padding=5, element_justification='center')
            if event == 'Next Page' and current_page < max_pages - 1:
                current_page += 1
                layout = update_layout(current_page)
                window.close()
                window = sg.Window('PsychoPass', layout, size=(1400, 825), icon=icon, use_ttk_buttons=True, ttk_theme=ttk_style, element_padding=5, element_justification='center')
            if event == 'Clear Passwords':
                Cells.remove_all_cells()
                sg.popup('All Passwords Removed.')
                window.close()
                PsychoPassGUI.mainmenu()
            if event == 'Save Password':
                window.close()
                PsychoPassGUI.passwordsavemenu(mode='save', table=None, source='passwordlist')
            if event == 'Back':
                window.close()
                PsychoPassGUI.mainmenu()
            for table in cell_tables:
                if event == f'-{table}_DELETE-':
                    print(f"Deleting {table}")
                    Cells.delete_cell(table)
                    sg.popup(f'{table} Deleted.')
                    window.close()
                    PsychoPassGUI.mainmenu()
                elif event == f'-{table}_EDIT-':
                    print(f"Editing {table}")
                    window.close()
                    PsychoPassGUI.passwordsavemenu(mode='edit', table=table, source='passwordlist')
    def GeneratePassword(source):
        key = DataBaseMG.get_table_value('Auth', 'Key')
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
                Cells.save_cell(values['-USERNAME-'], Password, values['-EMAIL-'], values['-WEBSITE-'], key)
                window['-USERNAME-'].update('')
                window['-EMAIL-'].update('')
                window['-WEBSITE-'].update('')
            if event == 'Back':
                window.close()
                source_function = getattr(PsychoPassGUI, source)
                source_function()
            elif event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
                
    def passwordsavemenu(mode, table, source):
        key = DataBaseMG.get_table_value("Auth", "Key")
        layout = [
            [sg.Text("PsychoPass Password Saving Menu")],
            [sg.Text("Username", size=7), sg.Input(key="-USERNAME-")],
            [sg.Text("Password", size=7), sg.Input(key="-PASSWORD-")],
            [sg.Text("Email", size=7), sg.Input(key="-EMAIL-")],
            [sg.Text("Website", size=7), sg.Input(key="-WEBSITE-")],
            [sg.Button("Save"), sg.Button('Generate'), sg.Button('Back')]
        ]
        dev_layout = [
            [sg.Text("Development Input: How many times to save the data?")],
            [sg.Input(key="-SAVE-COUNT-")],
            [sg.Button("Start Saving"), sg.Button("Cancel")]
        ]
        window = sg.Window('PsychoPass', layout, icon=icon, use_ttk_buttons=True, ttk_theme=ttk_style, element_padding=10, element_justification='center', finalize=True)
        dev_window = sg.Window('Development Input', dev_layout, icon=icon, use_ttk_buttons=True, ttk_theme=ttk_style, element_padding=10, element_justification='center', finalize=True)
        if mode == 'edit' and table:
            database_path = f"{root}/PsychoPassDB.db"
            with sqlite3.connect(database_path) as conn:
                cur = conn.cursor()
                cur.execute(f"SELECT Username, Password, Email, Website FROM {table}")
                cell_data = cur.fetchone()
                conn.close()
                if cell_data:
                    loaded_username, loaded_password, loaded_email, loaded_website = cell_data
                    window['-USERNAME-'].update(Cryptography.decrypt(loaded_username, key).decode())
                    window['-PASSWORD-'].update(Cryptography.decrypt(loaded_password, key).decode())
                    window['-EMAIL-'].update(Cryptography.decrypt(loaded_email, key).decode())
                    window['-WEBSITE-'].update(Cryptography.decrypt(loaded_website, key).decode())
        while True:
            event, values = window.read()
            event_dev, values_dev = dev_window.read()
            if event == 'Generate':
                window.close()
                PsychoPassGUI.GeneratePassword(source)
            if event_dev == 'Start Saving':
                dev_window.close()
                save_count = int(values_dev["-SAVE-COUNT-"])

                for _ in range(save_count):
                    username = values['-USERNAME-']
                    password = values['-PASSWORD-']
                    email = values['-EMAIL-']
                    website = values['-WEBSITE-']
                    if mode == 'save':
                        status = Cells.save_cell(username, password, email, website, key)
                    if mode == 'edit':
                        status = Cells.update_cell(table, username, password, email, website, key)
            if event_dev == 'Cancel' or event_dev == sg.WIN_CLOSED:
                dev_window.close()
            if event == 'Save':
                username = values['-USERNAME-']
                password = values['-PASSWORD-']
                email = values['-EMAIL-']
                website = values['-WEBSITE-']
                if mode == 'save':
                    status = Cells.save_cell(username, password, email, website, key)
                    if status == "Saved":
                        sg.popup("Successfully Saved!")
                    else:
                        sg.popup("An error has occured while saving your password!")
                if mode == 'edit':
                    status = Cells.update_cell(table, username, password, email, website, key)
                    if status == "Updated":
                        sg.popup("Successfully Updated!")
                    else:
                        sg.popup("An error has occured while updating your password!")
            if event == 'Back':
                window.close()
                source_function = getattr(PsychoPassGUI, source)
                source_function()
            if event == sg.WIN_CLOSED:
                sys.exit()
    def mainmenu():
        key = DataBaseMG.get_table_value("Auth", "Key")
        database_path = f"{root}/PsychoPassDB.db"
        DataBase = sqlite3.connect(database_path)
        cur = DataBase.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Cell%'")
        cell_tables = [row[0] for row in cur.fetchall() if row[0] != 'Cell0']
        cells_per_row = 5
        max_rows = 3
        max_display_cells = max_rows * cells_per_row
        rows = []
        cell_count = Cells.count_cells()
        if cell_count == 0:
            window_size = None
        if cell_count >= 1:
            window_size = (1400, 800)
        cell_count = min(cell_count, max_display_cells)
        if cell_count >= 15:
            passwords_button = sg.Button('Passwords')
        else:
            passwords_button = None
        for i in range(0, len(cell_tables), cells_per_row):
            if len(rows) >= max_rows:
                break
            row = []
            for table in cell_tables[i:i + cells_per_row]:
                cur.execute(f"SELECT Username, Password, Email, Website FROM {table}")
                cell_data = cur.fetchone()
                if cell_data:
                    username, password, email, website = cell_data
                    frame_key = f'-{table}_FRAME-'
                    cell_info = (
                        f"Username: {Cryptography.decrypt(username, key).decode()}\n"
                        f"Password: {Cryptography.decrypt(password, key).decode()}\n"
                        f"Email: {Cryptography.decrypt(email, key).decode()}\n"
                        f"Website: {Cryptography.decrypt(website, key).decode()}"
                    )
                    row.append(sg.Frame(table, [
                        [sg.Text(cell_info, size=(25, 5), pad=5)],
                        [sg.Button('Delete', key=f'-{table}_DELETE-', size=8, pad=5), sg.Button('Edit', key=f'-{table}_EDIT-', size=8, pad=5)]
                    ], size=(250, 165), key=frame_key, element_justification='center', pad=5))
            rows.append(row)     
        layout = [
            [sg.Image(logo)],
            [sg.Text('PsychoPass Main Menu', font=(35))],
        ]
        for row in rows:
            layout.append(row)
        if passwords_button:
            layout.append([sg.Button('Save Password'), sg.Button('Clear Passwords'), passwords_button, sg.Button('Options')])
        else:
            layout.append([sg.Button('Save Password'), sg.Button('Clear Passwords'), sg.Button('Options')])
        if window_size:
            window = sg.Window('PsychoPass', layout, size=window_size, icon=icon, use_ttk_buttons=True, ttk_theme=ttk_style, element_padding=5, element_justification='center')
        else:
            window = sg.Window('PsychoPass', layout, icon=icon, use_ttk_buttons=True, ttk_theme=ttk_style, element_padding=5, element_justification='center')
        print("Number of rows:", len(rows))
        print("Number of layout elements:", len(layout))
        DataBase.close()
        while True:
            event, values = window.read()
            if event == 'Options':
                window.close()
                PsychoPassGUI.options()
            if event == 'Passwords':
                window.close()
                PsychoPassGUI.passwordlist()
            if event == 'Clear Passwords':
                Cells.remove_all_cells()
                sg.popup('All Passwords Cleared')
                window.close()
                PsychoPassGUI.mainmenu()
            if event == 'Save Password':
                window.close()
                PsychoPassGUI.passwordsavemenu(mode='save', table=None, source='mainmenu')
            if event == sg.WIN_CLOSED:
                sys.exit()
            for table in cell_tables:
                if event == f'-{table}_DELETE-':
                    print(f"Deleting {table}")
                    Cells.delete_cell(table)
                    sg.popup(f'{table} Deleted.')
                    window.close()
                    PsychoPassGUI.mainmenu()
                elif event == f'-{table}_EDIT-':
                    print(f"Editing {table}")
                    window.close()
                    PsychoPassGUI.passwordsavemenu(mode='edit', table=table, source='mainmenu')

    def createaccount(type):
        if type == 'First Run':
            account_save = 'Create Account'
        if type == 'Change Auth':
            account_save = 'Change'
        layout = [
            [sg.Image(logo)],
            [sg.Text('Username'), sg.Input(key='-USERNAME-')],
            [sg.Text('Password'), sg.Input(key='-PASSWORD-', password_char='*')],
            [sg.Text('Re Enter Password'), sg.Input(key='-PASSWORD2-', password_char='*')],
            [sg.Button(account_save, key='-SAVE-'), sg.Button('Back')]
        ]
        window = sg.Window('PsychoPass', layout, icon=icon, use_ttk_buttons=True, ttk_theme=ttk_style, element_padding=5, element_justification='center')
        while True:
            event, values = window.read()
            if event == 'Back':
                window.close()
                PsychoPassGUI.login()
            if event == sg.WIN_CLOSED:
                sys.exit()
            if event == '-SAVE-':
                if type == 'First Run':
                    if values['-PASSWORD-'] == values ['-PASSWORD2-']:
                        key = Cryptography.gen_key()
                        username = Cryptography.encrypt(values['-USERNAME-'], key)
                        password = Cryptography.encrypt(values['-PASSWORD-'], key)
                        tuple = (username.decode(), password.decode(), key)
                        sg.popup(DataBaseMG.createauth(tuple), icon=icon, title='PsychoPass')
                        Json.PreLaunch()
                        Json.DateCheck()
                        window.close()
                        PsychoPassGUI.login()
                    else:
                        sg.popup('Passwords do not match.', icon=icon, title='PsychoPass')
                if type == 'Change Auth':
                    if values['-PASSWORD-'] == values ['-PASSWORD2-']:
                        key = DataBaseMG.get_table_value('Auth', 'Key')
                        username = Cryptography.encrypt(values['-USERNAME-'], key)
                        password = Cryptography.encrypt(values['-PASSWORD-'], key)
                        DataBaseMG.update_table('Auth', 'Username', username)
                        DataBaseMG.update_table('Auth', 'Password', password)
                        sg.popup('Account Login Changes Saved!')
                        window.close()
                        PsychoPassGUI.login()
                    else:
                        sg.popup('Passwords do not match.', icon=icon, title='PsychoPass')

        window.close()
    def forgotpassword():
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
                Auth = QR.CheckQR(values['-KEY-'])
                if Auth is True:
                    window.close()
                    PsychoPassGUI.createaccount('Change Auth')
                else:
                    sg.popup('Incorrect Code.', icon=icon, title='PsychoPass')
            if event == 'Back':
                window.close()
                PsychoPassGUI.login()
            if event == sg.WIN_CLOSED:
                sys.exit()
    def login():
        layout = [
            [sg.Image(logo)],
            [sg.Text('PsychoPass Login', font=(20))],
            [sg.Text('Username'), sg.Input(key='-USERNAME-')],
            [sg.Text('Password'), sg.Input(key='-PASSWORD-', password_char='*')],
            [sg.Button('Login'), sg.Button('Create Account'), sg.Button('Forgot Password')]
        ]
        window = sg.Window('PsychoPass', layout, element_padding=(5,5), element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style, icon=icon)
        while True:
            event, values = window.read()
            if event == 'Forgot Password':
                window.close()
                PsychoPassGUI.forgotpassword()
            if event == 'Login':
                if DataBaseMG.is_value("Auth", "Password") is True and DataBaseMG.is_value("Auth", "Username") is True:
                    username = values['-USERNAME-']
                    password = values['-PASSWORD-']
                    Auth = DataBaseMG.login(username, password)
                    if Auth is True:
                        print("Logged in!")
                        window.close()
                        PsychoPassGUI.mainmenu()
                    if Auth is False:
                        sg.popup("Login information invalid. Please check the username and password and try again.", icon=icon, title='PsychoPass')
                if DataBaseMG.is_value("Auth", "Password") is False and DataBaseMG.is_value("Auth", "Username") is False:
                    sg.popup("Please create an account.", icon=icon, title='PsychoPass')
            if event == sg.WIN_CLOSED:
                sys.exit()
            elif event == 'Create Account':
                if DataBaseMG.is_value("Auth", "Password") is True and DataBaseMG.is_value("Auth", "Username") is True:
                    sg.popup("Account Already Created.", icon=icon, title='PsychoPass')
                if DataBaseMG.is_value("Auth", "Password") is False and DataBaseMG.is_value("Auth", "Username") is False:
                    window.close()
                    PsychoPassGUI.createaccount(type='First Run')
DataBaseMG.init()

if os.path.exists(JsonPath):
    AutoLogin = Json.AutoLogin(check=True)
    if AutoLogin == 'True':
        PsychoPassGUI.mainmenu()
    if AutoLogin == 'False':
        PsychoPassGUI.login()
else:
    PsychoPassGUI.login()