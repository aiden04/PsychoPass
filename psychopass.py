import PySimpleGUI as sg
import os, time, sys, webbrowser
from utils import *

class PsychoPass:
    def __init__(self, db_path, verbose=False):
        self.verbose = verbose
        self.db_path = db_path
        self.Cipher = Cipher(db_path, verbose=self.verbose)
        self.ttk_style = "clam"
        self.debug = sg.show_debugger_window()
        if self.Cipher.SQLite.checkTable("users") is False:
            self.register()
        else:
            self.main()

    def main(self):
        layout = [
            [sg.Text("PsychoPass", font=("Helvetica", 25))],
            [sg.Text("Username: "), sg.InputText(key="username")],
            [sg.Text("Password: "), sg.InputText(key="password", password_char="*")],
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
            [sg.Text("PsychoPass", font=("Helvetica", 25))],
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
            [
                sg.Column([
                    [sg.Text("DataBase Path: ", font=("Helvetica", 10), pad=5)],
                    [sg.Text(self.db_path, font=("Helvetica", 10), pad=5)]
                ], justification="center", element_justification="center")
            ],
            [
                sg.Column([
                    [sg.Button("Passwords", size=(10, 1))],
                    [sg.Button("Settings", size=(10, 1))],
                    [sg.Button("Logout", size=(10, 1))]
                ], justification="left", element_justification="left"),
                sg.Column([
                    [sg.Text("Logged in as: {}".format(self.Cipher.decrypt(self.Cipher.SQLite.getUsername())), font=("Helvetica", 10))],
                    [sg.Text(time.strftime("%m/%d/%Y %H:%M:%S"), font=("Helvetica", 10), key="-TIME-")],
                    [sg.Text("{} Passwords Saved".format(len(self.Cipher.SQLite.countCellTables())), font=("Helvetica", 10))],
                    [sg.Text("About", font=("Helvetica", 10), text_color="blue", enable_events=True, key="-LINK-")],
                ], justification="center", element_justification="center", pad=5)
            ]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", element_padding=5, use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read(timeout=1000)  # Add timeout parameter
            if event == sg.WIN_CLOSED:
                break
            if event == "Passwords":
                window.close()
                self.passwordMenu()
            if event == "Logout":
                window.close()
                self.main()
            elif event == "-LINK-":
                webbrowser.open_new_tab("https://github.com/aiden04/PsychoPass")
            window["-TIME-"].update(time.strftime("%m/%d/%Y %H:%M:%S"))
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
        layout = [[sg.Text("PsychoPass", font=("Helvetica", 25))]]
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
                                    sg.Text("Website:", text_color="white"),
                                    sg.Text(website_text, text_color="blue", justification="left", enable_events=True, key=f"link{cell_num}")
                                ],
                                [sg.Button(f"Edit", key=f"edit{cell_num}", size=(8, 1)), sg.Button(f"Delete", key=f"delete{cell_num}", size=(8, 1))]
                            ], size=(250, 165), key=f"frame{cell_num}", element_justification="center", pad=10)
                        )
                    else:
                        row.append(
                            sg.Frame(self.Cipher.decrypt(platform), [
                                [sg.Text(f"Username: {self.Cipher.decrypt(username)}", justification="left")],
                                [sg.Text("Password: **********", justification="left")],
                                [sg.Text(f"Email: {self.Cipher.decrypt(email)}", justification="left")],
                                [
                                    sg.Text("Website:", text_color="white"),
                                    sg.Text(website_text, text_color="blue", justification="left", enable_events=True, key=f"link{cell_num}")
                                ],
                                [sg.Button(f"Edit", key=f"edit{cell_num}", size=(8, 1)), sg.Button(f"Delete", key=f"delete{cell_num}", size=(8, 1))]
                            ], size=(250, 165), key=f"frame{cell_num}", element_justification="center", pad=10)
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
                window.hide()
                self.addPassword()
                window.un_hide()
            elif event == "Home":
                window.close()
                self.home()
            elif event == "Search":
                query = values["query"]
                if query:
                    window.hide()
                    self.search(query)
                    window.un_hide()
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
                            ], size=(250, 165), element_justification="center", pad=10)
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
                            ], size=(250, 165), element_justification="center", pad=10)
                        )
            layout.append(row)
        if show_passwords is True: button_text = "Hide Passwords"
        if show_passwords is False: button_text = "Show Passwords"
        layout.append([sg.Button("Back", size=(14, 1)), sg.Button("Add Password", size=(14, 1)), sg.Button("Clear Passwords", size=(14, 1)), sg.Button(button_text, size=(14, 1), key="password_rotator"), sg.Button("Next", size=(14, 1))])
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                window.close()
                break
            elif event == "Back":
                window.close()
                self.passwordMenu()
            elif event == "password_rotator":
                if show_passwords is True:
                    window.close()
                    self.search(query, int=int, show_passwords=not show_passwords)
                elif show_passwords is False:
                    window.close()
                    self.search(query, int=int, show_passwords=not show_passwords)
            elif event == "Add Password":
                window.hide()
                self.addPassword()
                window.refresh()
                window.un_hide()
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
            elif event == "Home":
                window.close()
                self.home()
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
                    window.hide()
                    self.addPassword(cell=cell[0])
                    window.un_hide()
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
            [sg.Text("Platform: "), sg.InputText(key="platform")],
            [sg.Text("Username: "), sg.InputText(key="username")],
            [sg.Text("Password: "), sg.InputText(key="password")],
            [sg.Text("Email: "), sg.InputText(key="email")],
            [sg.Text("Website: "), sg.InputText(key="website")],
            [sg.Button("Save Password"), sg.Button("Back")]
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
            elif event == "Back":
                window.close()
            elif event == "Save Password":
                if cell:
                    if all(values.values()):
                        platform, username, password, email, website = self.Cipher.encrypt(values["platform"]), self.Cipher.encrypt(values["username"]), self.Cipher.encrypt(values["password"]), self.Cipher.encrypt(values["email"]), self.Cipher.encrypt(values["website"])
                        self.Cipher.SQLite.editPassword(cell, platform, username, password, email, website)
                        sg.popup("Password edited successfully!")
                        window.close()
                    else:
                        sg.popup("Please fill out all fields!")
                else:
                    if all(values.values()):
                        platform, username, password, email, website = self.Cipher.encrypt(values["platform"]), self.Cipher.encrypt(values["username"]), self.Cipher.encrypt(values["password"]), self.Cipher.encrypt(values["email"]), self.Cipher.encrypt(values["website"])
                        self.Cipher.SQLite.addPassword(platform, username, password, email, website)
                        sg.popup("Password added successfully!")
                        for key in values:
                            window.Element(key).Update("")
                    else:
                        sg.popup("Please fill out all fields!")
        window.close()
