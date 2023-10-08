import PySimpleGUI as sg
import os, time, sys, webbrowser, configparser, shutil, requests
from utils import *

class PsychoPass:
    def __init__(self, db_path, verbose=False):
        self.verbose = verbose
        self.db_path = db_path
        self.Cipher = Cipher(db_path, verbose=self.verbose)
        self.ttk_style = "clam"
        sg.SetGlobalIcon(f"{os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'assets/icon.ico'))}")
        sg.theme("SystemDefault")
        self.logo = f"{os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'assets/logo.png'))}"
        self.debug = sg.show_debugger_window()
        if self.Cipher.SQLite.checkTable("users") is False:
            self.register()
        else:
            self.main()

    def authenticate(self, direct=""):
        self.direct = direct
        layout = [
        [sg.Image(self.logo)],
        [sg.Text("Authenticate", font=("Helvetica", 25))],
        [sg.Text("Username: ", size=8), sg.Input(key="username")],
        [sg.Text("Password: ", size=8), sg.Input(key="password", password_char="*")],
        [sg.Button("Authenticate"), sg.Button("Cancel")]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == "Cancel":
                break
            elif event == sg.WIN_CLOSED:
                sys.exit()
            elif event == "Authenticate":
                if self.Cipher.checkLogin(values["username"], values["password"]) is True:
                    window.close()
                    self.direct()
                else:
                    sg.popup("Authentication failed!")
        window.close()

    def changeLogin(self):
        layout = [
            [sg.Image(self.logo)],
            [sg.Text("Change Login", font=("Helvetica", 25))],
            [sg.Text("Username: ", size=16), sg.Input(key="username")],
            [sg.Text("Password: ", size=16), sg.Input(key="password", password_char="*")],
            [sg.Text("Re Enter Password: ", size=16), sg.Input(key="password2", password_char="*")],
            [sg.Button("Change Login"), sg.Button("Cancel")]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                sys.exit()
            elif event == "Cancel":
                window.close()
                self.options()
            elif event == "Change Login":
                if values["password"] == values["password2"]:
                    username, password = self.Cipher.encrypt(values["username"]), self.Cipher.encrypt(values["password"])
                    self.Cipher.SQLite.editUser(username, password)
                    sg.popup("Login changed successfully!")
                    window.close()
                    self.options()
                else:
                    sg.popup("Passwords do not match!")

    def changeDatabasePath(self):
        layout = [
            [sg.Image(self.logo)],
            [sg.Text("Change Database Path", font=("Helvetica", 25))],
            [sg.Text("New Database Path: ", size=16), sg.Input(key="db_path"), sg.FileBrowse(file_types=(("Database File", "*.db")), key="db_path_browse")],
            [sg.Button("Change Database Path"), sg.Button("Cancel")]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                sys.exit()
            elif event == "Cancel":
                window.close()
                self.options()
            elif event == "Change Database Path":
                db_path = values["db_path"]
                if os.path.isfile(db_path) is False:
                    if self.verbose is True: print("Database not found")
                    popup = sg.popup("Database not found! Would you like to copy the current database to the new path?", title="Database Not Found", custom_text=("Yes", "No"))
                    if popup == "Yes":
                        if self.verbose is True: print("Copying database to path: {}".format(db_path))
                        shutil.copyfile(self.db_path, db_path)
                        config = configparser.ConfigParser()
                        config.read('config.ini')
                        config['DEFAULT'] = {'db_path': db_path}
                        with open('config.ini', 'w') as configfile:
                            config.write(configfile)
                        sg.popup("Database path changed successfully!")
                        window.close()
                        PsychoPass(db_path=db_path, verbose=self.verbose)
                    else:
                        if self.verbose is True: print("Creating new database.")
                        with open(db_path, "w"):
                            if self.verbose is True: print("Created new database at: {}.".format(db_path))
                        config = configparser.ConfigParser()
                        config.read('config.ini')
                        config['DEFAULT'] = {'db_path': db_path}
                        with open('config.ini', 'w') as configfile:
                            config.write(configfile)
                        sg.popup("Database path changed successfully!")
                        window.close()
                        self.options()
                else:
                    if self.verbose is True: print("Database found at: {}".format(db_path))
                    config = configparser.ConfigParser()
                    config.read('config.ini')
                    config['DEFAULT'] = {'db_path': db_path}
                    with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                    sg.popup("Database path changed successfully!")
                    window.close()
                    PsychoPass(db_path=db_path, verbose=self.verbose)

    def options(self):
        layout = [
            [sg.Image(self.logo)],
            [sg.Text("Options", font=("Helvetica", 25))],
            [sg.Button("Change Login"), sg.Button("Change Database Path"), sg.Button("Back")]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                sys.exit()
            elif event == "Back":
                window.close()
                self.home()
            elif event == "Change Login":
                window.close()
                self.authenticate(direct=self.changeLogin)
            elif event == "Change Database Path":
                window.close()
                self.authenticate(direct=self.changeDatabasePath)
        window.close()

    def main(self):
        layout = [
            [sg.Image(self.logo)],
            [sg.Text("Username: ", size=8), sg.InputText(key="username")],
            [sg.Text("Password: ", size=8), sg.InputText(key="password", password_char="*")],
            [sg.Button("Login"), sg.Button("Register")]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        if self.verbose is True: self.debug
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Login":
                if self.Cipher.checkLogin(values["username"], values["password"]) is True:
                    window.close()
                    self.home()
                else:
                    sg.popup("Login failed!")
            elif event == "Register":
                window.close()
                self.register()
        window.close()

    def register(self):
        layout = [
            [sg.Image(self.logo)],
            [sg.Text("Username: "), sg.InputText(key="username")],
            [sg.Text("Password: "), sg.InputText(key="password", password_char="*")],
            [sg.Button("Register"), sg.Button("Cancel")]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == "Cancel":
                break
            elif event == "Register":
                username, password = self.Cipher.encrypt(values["username"]), self.Cipher.encrypt(values["password"])
                self.Cipher.SQLite.registerUser(username, password)
                sg.popup("User registered successfully!")
                window.close()
                self.main()
        window.close()

    def home(self):
        layout = [
            [sg.Column([[sg.Image(self.logo)]], justification="center", element_justification="center")],
            [
                sg.Column([
                    [sg.Button("Passwords", size=(10, 1))],
                    [sg.Button("Settings", size=(10, 1))],
                    [sg.Button("Update", size=(10, 1))],
                    [sg.Button("Logout", size=(10, 1))]
                ], justification="left"),
                sg.Column([
                    [sg.Text("Logged in as: {}".format(self.Cipher.decrypt(self.Cipher.SQLite.getUsername())), font=("Helvetica", 10))],
                    [sg.Text(time.strftime("%m/%d/%Y %H:%M:%S"), font=("Helvetica", 10), key="-TIME-")],
                    [sg.Text("DataBase Path:", font=("Helvetica", 10))],
                    [sg.Text(self.db_path, font=("Helvetica", 10), pad=5)],
                    [sg.Text("{} Passwords Saved".format(len(self.Cipher.SQLite.countCellTables())), font=("Helvetica", 10))],
                    [sg.Text("About", font=("Helvetica", 10), text_color="blue", enable_events=True, key="-LINK-")],
                ], justification="center", element_justification="center", expand_x=1)
            ]
        ]
        window = sg.Window("PsychoPass", layout, element_padding=5, use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read(timeout=1000)
            if event == sg.WIN_CLOSED:
                break
            elif event == "Update":
                window.hide()
                self.update()
                window.un_hide()
            if event == "Passwords":
                window.close()
                self.passwordMenu()
            if event == "Logout":
                window.close()
                self.main()
            if event == "Settings":
                window.close()
                self.options()
            elif event == "-LINK-":
                webbrowser.open_new_tab("https://github.com/aiden04/PsychoPass")
            window["-TIME-"].update(time.strftime("%m/%d/%Y %H:%M:%S"))
        window.close()

    def update(self):
        update = Update(verbose=self.verbose)
        layout = [
            [sg.Image(self.logo)],
            [sg.Text("Update", font=("Helvetica", 25))],
            [sg.Text("Current Version: 1.5.3b", size=16)],
            [sg.Text("Checking for updates...", key="update_text")],
            [sg.ProgressBar(100, orientation="h", size=(20, 20), key="progress")],
            [sg.Button("Update"), sg.Button("Cancel"), sg.Button("Show Console")],
            [sg.Multiline("", size=(80, 10), key="console", visible=False, enable_events=True, autoscroll=True, reroute_stdout=True, write_only=True)]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style, finalize=True)
        progress_bar = window["progress"]
        progress_bar.update_bar(0)
        console = window["console"]
        while True:
            event, values = window.read(timeout=100)
            if event == sg.WIN_CLOSED:
                sys.exit()
            elif window["update_text"].get() == "Checking for updates...":
                if update.checkForUpdate() is True:
                    window["update_text"].update("Update Available!")
                if update.checkForUpdate() is False:
                    window["update_text"].update("No Update Available.")
            elif event == "Cancel":
                window.close()
                self.home()
            elif event == "Update":
                window["Update"].update("Updating")
                window["Update"].update(disabled=True)
                progress_thread = threading.Thread(target=update.run_update, args=(window,))
                progress_thread.start()
                while progress_thread.is_alive():
                    event, values = window.read(timeout=100)
                    if event == sg.WIN_CLOSED:
                        sys.exit()
                window["update_text"].update("Update complete!")
                time.sleep(1)
                window["update_text"].update("Cleaning up...")
                update.cleanup()
                window["update_text"].update("Done!")
                sg.popup("Update complete! Psychopass must now restart")
                sys.exit()
            elif event == "Show Console":
                console = window["console"]
                console.update(visible=not console.visible)
                if console.visible:
                    console.update(value=console.get())
        window.close()

    def passwordMenu(self, int=0, show_passwords=False):
        if self.verbose is True: print("Opening password menu with page {}.".format(int))
        max_frames_per_page = 15
        num_columns = 5
        num_rows = 3
        cells = self.Cipher.SQLite.countCellTables()
        num_frames = len(cells)
        start_index = int * max_frames_per_page
        end_index = min(start_index + max_frames_per_page, num_frames)
        frames_to_display = cells[start_index:end_index]
        layout = [[sg.Image(self.logo)], [sg.Text("Passwords", font=("Helvetica", 25))]]
        for i in range(num_rows):
            row = []
            for j in range(num_columns):
                index = i * num_columns + j
                if index < len(frames_to_display):
                    cell_num = frames_to_display[index]
                    platform, username, password, email, website = self.Cipher.SQLite.readCell(cell_num)
                    website_text = self.Cipher.decrypt(website)
                    
                    if show_passwords:
                        row.append(
                            sg.Frame(self.Cipher.decrypt(platform), [
                                [sg.Text(f"Username: {self.Cipher.decrypt(username)}", justification="left")],
                                [sg.Text(f"Password: {self.Cipher.decrypt(password)}", justification="left")],
                                [sg.Text(f"Email: {self.Cipher.decrypt(email)}", justification="left")],
                                [
                                    sg.Text("Website:", justification="left"),
                                    sg.Text(website_text, text_color="blue", justification="left", enable_events=True, key=f"link{cell_num}")
                                ],
                                [sg.Button(f"Edit", key=f"edit{cell_num}", size=(8, 1)), sg.Button(f"Delete", key=f"delete{cell_num}", size=(8, 1))]
                            ], size=(250, 165), key=f"frame{cell_num}", element_justification="center", pad=10, relief="solid")
                        )
                    else:
                        row.append(
                            sg.Frame(self.Cipher.decrypt(platform), [
                                [sg.Text(f"Username: {self.Cipher.decrypt(username)}", justification="left")],
                                [sg.Text("Password: **********", justification="left")],
                                [sg.Text(f"Email: {self.Cipher.decrypt(email)}", justification="left")],
                                [
                                    sg.Text("Website:", justification="left"),
                                    sg.Text(website_text, text_color="blue", justification="left", enable_events=True, key=f"link{cell_num}")
                                ],
                                [sg.Button(f"Edit", key=f"edit{cell_num}", size=(8, 1)), sg.Button(f"Delete", key=f"delete{cell_num}", size=(8, 1))]
                            ], size=(250, 165), key=f"frame{cell_num}", element_justification="center", pad=10, relief="solid")
                    )
                else:
                    pass
            layout.append(row)
        back_button_disabled = int == 0
        if back_button_disabled:
            if int == 0: back_button_disabled = True
            else: back_button_disabled = False
        if self.verbose is True: print("Frames to display: ", len(frames_to_display))
        if len(frames_to_display) < 15: next_button_disabled = True
        else: next_button_disabled = False
        if show_passwords is True: button_text = "Hide Passwords"
        if show_passwords is False: button_text = "Show Passwords"
        layout.append([sg.Input(key="query", size=(25, 1)), sg.Button("Search", size=(8, 1))])
        layout.append([sg.Button("Back", size=(14, 1), key="back", disabled=back_button_disabled), sg.Button("Add Password", size=(14, 1)), sg.Button("Clear Passwords", size=(14, 1)), sg.Button("Home", size=(14, 1)), sg.Button(button_text, key="-SHOW-", size=(14, 1)), sg.Button("Next", size=(14, 1))])  # Change the checkbox to a button
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                sys.exit()
            elif event == "back":
                window.close()
                self.passwordMenu(int=int-1, show_passwords=show_passwords)
            elif event == "Next":
                window.close()
                self.passwordMenu(int=int+1, show_passwords=show_passwords)
            elif event == "Add Password":
                window.close()
                self.addPassword()
                self.passwordMenu(int=int, show_passwords=show_passwords)
            elif event == "Home":
                window.close()
                self.home()
            elif event == "Search":
                query = values["query"]
                if query:
                    window.close()
                    self.search(query, show_passwords=show_passwords)
            elif event == "Clear Passwords":
                popup = sg.popup("Are you sure you want to clear all passwords?", title="Clear Passwords", custom_text=("Yes", "No"))
                if popup == "Yes":
                    for cell in cells:
                        self.Cipher.SQLite.cur.execute(f"DROP TABLE cell{cell}")
                        if self.verbose is True: print("Deleted cell{}.".format(cell))
                        self.Cipher.SQLite.conn.commit()
                    sg.popup("Passwords cleared successfully!")
                    window.close()
                    self.passwordMenu(int=int, show_passwords=show_passwords)
                else:
                    pass
            for cell in cells:
                if event == f"delete{cell}":
                    platform, _, _, _, _, = self.Cipher.SQLite.readCell(cell)
                    popup = sg.popup("Are you sure you want to delete the password for {}?".format(self.Cipher.decrypt(platform)), title="Delete Password", custom_text=("Yes", "No"))
                    if popup == "Yes":
                        self.Cipher.SQLite.cur.execute(f"DROP TABLE cell{cell}")
                        if self.verbose is True: print("Deleted cell{}.".format(cell))
                        self.Cipher.SQLite.conn.commit()
                        sg.popup("Password deleted successfully!")
                        window.close()
                        self.passwordMenu(int=int, show_passwords=show_passwords)
                    else:
                        pass
                if event == f"edit{cell}":
                    window.close()
                    self.addPassword(cell=cell)
                if event == "-SHOW-":
                    show_passwords = not show_passwords  # Toggle the show_passwords variable
                    window.close()
                    self.passwordMenu(int=int, show_passwords=show_passwords)
                if event == f"link{cell}":
                    _, _, _, _, website = self.Cipher.SQLite.readCell(cell)
                    webbrowser.open_new_tab(self.Cipher.decrypt(website))
        window.close()
    
    def search(self, query, int=0, show_passwords=False):
        if self.verbose is True: print("Searching for {}.".format(query))
        results = self.Cipher.queryCells(query)
        layout = []
        layout.append([sg.Text("Search Results", font=("Helvetica", 25))])
        if self.verbose is True: print("Results: ", len(results))
        max_frames_per_page = 15
        num_columns = 5
        num_rows = 3
        num_frames = len(results)
        start_index = int * max_frames_per_page
        end_index = min(start_index + max_frames_per_page, num_frames)
        frames_to_display = results[start_index:end_index]
        for i in range(num_rows):
            row = []
            for j in range(num_columns):
                index = i * num_columns + j
                if index < len(frames_to_display):
                    cell = results[index]
                    if show_passwords is True:
                        cell, platform, username, password, email, website = cell[0], cell[1], cell[2], cell[3], cell[4], cell[5]
                        row.append(
                            sg.Frame(platform, [
                                [sg.Text(f"Username: {username}", justification="left")],
                                [sg.Text(f"Password: {password}", justification="left")],
                                [sg.Text(f"Email: {email}", justification="left")],
                                [
                                    sg.Text("Website:", text_color="white"),
                                    sg.Text(website, text_color="blue", justification="left", enable_events=True, key=f"link{cell}")
                                ],
                                [sg.Button(f"Edit", key=f"edit{cell}", size=(8, 1)), sg.Button(f"Delete", key=f"delete{cell}", size=(8, 1))]
                            ], size=(250, 165), element_justification="center", pad=10, relief="solid")
                        )
                    else:
                        cell, platform, username, password, email, website = cell[0], cell[1], cell[2], cell[3], cell[4], cell[5]
                        row.append(
                            sg.Frame(platform, [
                                [sg.Text(f"Username: {username}", justification="left")],
                                [sg.Text(f"Password: **********", justification="left")],
                                [sg.Text(f"Email: {email}", justification="left")],
                                [
                                    sg.Text("Website:", text_color="white"),
                                    sg.Text(website, text_color="blue", justification="left", enable_events=True, key=f"link{cell}")
                                ],
                                [sg.Button(f"Edit", key=f"edit{cell}", size=(8, 1)), sg.Button(f"Delete", key=f"delete{cell}", size=(8, 1))]
                            ], size=(250, 165), element_justification="center", pad=10, relief="solid")
                        )
            layout.append(row)
        if show_passwords is True: button_text = "Hide Passwords"
        if show_passwords is False: button_text = "Show Passwords"
        layout.append([sg.Button("Back", size=(14, 1)), sg.Button("Add Password", size=(14, 1)), sg.Button("Clear Passwords", size=(14, 1)), sg.Button(button_text, size=(14, 1), key="password_rotator"), sg.Button("Next", size=(14, 1))])
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                sys.exit()
            elif event == "Back":
                if int == 0:
                    window.close()
                    self.passwordMenu(show_passwords=show_passwords)
                else:
                    window.close()
                    self.search(query, int=int-1, show_passwords=show_passwords)
            elif event == "password_rotator":
                if show_passwords is True:
                    window.close()
                    self.search(query, int=int, show_passwords=not show_passwords)
                elif show_passwords is False:
                    window.close()
                    self.search(query, int=int, show_passwords=not show_passwords)
            elif event == "Add Password":
                window.close()
                self.addPassword()
                self.search(query, int=int, show_passwords=show_passwords)
                
            elif event == "Clear Passwords":
                popup = sg.popup("Are you sure you want to delete all passwords?", title="Clear Passwords", custom_text=("Yes", "No"))
                if popup == "Yes":
                    for cell in results:
                        self.Cipher.SQLite.cur.execute(f"DROP TABLE cell{cell[0]}")
                        if self.verbose is True: print("Deleted cell{}.".format(cell[0]))
                        self.Cipher.SQLite.conn.commit()
                    sg.popup("Passwords deleted successfully!")
                    window.close()
                    self.search(query)
                else:
                    pass
            elif event == "Next":
                window.close()
                self.search(query, int=int+1, show_passwords=show_passwords)
            for cell in results:
                if event == f"delete{cell[0]}":
                    platform = cell[0]
                    popup = sg.popup("Are you sure you want to delete the password for {}?".format(platform), title="Delete Password", custom_text=("Yes", "No"))
                    if popup == "Yes":
                        self.Cipher.SQLite.cur.execute(f"DROP TABLE cell{cell[0]}")
                        if self.verbose is True: print("Deleted cell{}.".format(cell[0]))
                        self.Cipher.SQLite.conn.commit()
                        sg.popup("Password deleted successfully!")
                        window.close()
                        self.search(query)
                    else:
                        pass
                elif event == f"edit{cell[0]}":
                    window.close()
                    self.addPassword(cell=cell[0])
                    self.search(query, int=int, show_passwords=show_passwords)
                elif event == f"link{cell[5]}":
                    print(cell[5])
                    website = self.Cipher.SQLite.readCell(cell)[5]
                    webbrowser.open_new_tab(website)
            window.refresh()
        window.close()

    def addPassword(self, cell=None):
        layout = [
            [sg.Text("PsychoPass", font=("Helvetica", 25))],
            [sg.Text("Add Password")],
            [sg.Text("Platform: ", size=8), sg.InputText(key="platform")],
            [sg.Text("Username: ", size=8), sg.InputText(key="username")],
            [sg.Text("Password: ", size=8), sg.InputText(key="password")],
            [sg.Text("Email: ", size=8), sg.InputText(key="email")],
            [sg.Text("Website: ", size=8), sg.InputText(key="website")],
            [sg.Button("Save Password", size=17), sg.Button("Generate Password", size=17), sg.Button("Back", size=17)]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style, finalize=True)
        if cell:
            platform, username, password, email, website = self.Cipher.SQLite.readCell(cell)
            window["platform"].update(self.Cipher.decrypt(platform))
            window["username"].update(self.Cipher.decrypt(username))
            window["password"].update(self.Cipher.decrypt(password))
            window["email"].update(self.Cipher.decrypt(email))
            window["website"].update(self.Cipher.decrypt(website))
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Generate Password":
                window["password"].update(self.Cipher.generatePassword())
            elif event == "Back":
                window.close()
            elif event == "Save Password":
                if cell:
                    if all(values.values()):
                        platform, username, password, email, website = self.Cipher.encrypt(values["platform"]), self.Cipher.encrypt(values["username"]), self.Cipher.encrypt(values["password"]), self.Cipher.encrypt(values["email"]), self.Cipher.encrypt(values["website"])
                        self.Cipher.SQLite.editPassword(cell, platform, username, password, email, website)
                        sg.popup("Password edited successfully!")
                        window.close()
                        self.passwordMenu()
                    else:
                        sg.popup("Please fill out all fields!")
                else:
                    if all(values.values()):
                        platform, username, password, email, website = self.Cipher.encrypt(values["platform"]), self.Cipher.encrypt(values["username"]), self.Cipher.encrypt(values["password"]), self.Cipher.encrypt(values["email"]), self.Cipher.encrypt(values["website"])
                        self.Cipher.SQLite.addPassword(platform, username, password, email, website)
                        sg.popup("Password added successfully!")
                        for value in values:
                            window[value].update("")
                    else:
                        sg.popup("Please fill out all fields!")
        window.close()
