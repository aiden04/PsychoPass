import PySimpleGUI as sg
import os, time, sys, webbrowser
from utils import *

class PsychoPass:
    def __init__(self, db_path, verbose=False):
        self.verbose = verbose
        self.db_path = db_path
        self.Cipher = Cipher(db_path, verbose=self.verbose)
        self.ttk_style = "clam"
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
            elif event == "-LINK-":
                webbrowser.open_new_tab("https://github.com/aiden04/PsychoPass")
            window["-TIME-"].update(time.strftime("%m/%d/%Y %H:%M:%S"))
        window.close()


    def createCellFrame(self, cell):
        cell_data = self.Cipher.SQLite.readCell(cell)
        cell_layout = (
            f"Username: {self.Cipher.decrypt(cell_data[1])}\n"
            f"Password: {self.Cipher.decrypt(cell_data[2])}\n"
            f"Email: {self.Cipher.decrypt(cell_data[3])}\n"
            f"Website: {self.Cipher.decrypt(cell_data[4])}"
        )
        frame = sg.Frame(self.Cipher.decrypt(cell_data[0]), [[sg.Text(cell_layout, size=(25, 5), pad=5)], [sg.Button("Delete", key=f"delete{cell}", size=8), sg.Button("Edit", key=f"edit{cell}", size=8)]], size=(250, 165), key=f"frame{cell}", element_justification='center', pad=10)
        return frame

    def passwordMenu(self, int=0):
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
                    row.append(self.createCellFrame(frames_to_display[index]))
                else:
                    pass
            layout.append(row)
        back_button_disabled = int == 0
        if back_button_disabled:
            if int == 0: back_button_disabled = True
            else: back_button_disabled = False
        if len(cells) < 15: next_button_disabled = True
        else: next_button_disabled = False
        layout.append([sg.Button("Back", size=(12, 1), key="back", disabled=back_button_disabled), sg.Button("Add Password", size=(12, 1)), sg.Button("Home", size=(12, 1)), sg.Button("Next", size=(12, 1), disabled=next_button_disabled)])
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "back":
                window.close()
                self.passwordMenu(int=int-1)
            elif event == "Next":
                window.close()
                self.passwordMenu(int=int+1)
            elif event == "Add Password":
                window.close()
                self.addPassword()
            elif event == "Home":
                window.close()
                self.home()
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
                        self.passwordMenu(int=int)
                    else:
                        pass
                elif event == f"edit{cell}":
                    window.close()
                    self.editPassword(cell)
    
    def addPassword(self):
        layout = [
            [sg.Text("PsychoPass", font=("Helvetica", 25))],
            [sg.Text("Add Password")],
            [sg.Text("Platform: "), sg.InputText(key="platform")],
            [sg.Text("Username: "), sg.InputText(key="username")],
            [sg.Text("Password: "), sg.InputText(key="password")],
            [sg.Text("Email: "), sg.InputText(key="email")],
            [sg.Text("Website: "), sg.InputText(key="website")],
            [sg.Button("Add Password"), sg.Button("Back")]
        ]
        window = sg.Window("PsychoPass", layout, element_justification="center", use_ttk_buttons=True, ttk_theme=self.ttk_style)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == "Back":
                break
            elif event == "Add Password":
                if all(values.values()):
                    platform, username, password, email, website = self.Cipher.encrypt(values["platform"]), self.Cipher.encrypt(values["username"]), self.Cipher.encrypt(values["password"]), self.Cipher.encrypt(values["email"]), self.Cipher.encrypt(values["website"])
                    self.Cipher.SQLite.addPassword(platform, username, password, email, website)
                    sg.popup("Password added successfully!")
                    for key in values:
                        window.Element(key).Update("")
                else:
                    sg.popup("Please fill out all fields!")
        window.close()