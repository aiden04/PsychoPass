import PySimpleGUI as sg
import sys
import random
from src.home import Home
from src.createLogin import CreateLogin
from src.configuration.jsonManagement import ReadSettings, JsonPath
from src.configuration.utils import decryptString, KEY, savedLogin, ttk_style

themes = ['bright', 'brown', 'red', 'orange', 'yellow', 'green', 'light', 'lightgrey', 'lightgreen', 'lightblue', 'SystemDefault']
theme = random.choice(themes)

def Login():
    sg.theme(theme)
    layout = [
        [sg.Text('PsychoPass Login', size=(20, 1), font=('Helvetica', 20), justification='center')],
        [sg.Text('Username:', size=(12, 1), font=('Helvetica', 12)), 
         sg.Input(key='-USERNAME-', size=(20, 1), font=('Helvetica', 12))],
        [sg.Text('Password:', size=(12, 1), font=('Helvetica', 12)), 
         sg.Input(key='-PASSWORD-', size=(20, 1), font=('Helvetica', 12), password_char='*')],
        [sg.Button('Login', size=(10, 1), font=('Helvetica', 12)), 
         sg.Button('Create Login', size=(10, 1), font=('Helvetica', 12))]
    ]

    window = sg.Window('PsychoPass Login', layout, element_justification='center', margins=(20, 20), use_ttk_buttons=True, ttk_theme=ttk_style)

    while True:
        event, values = window.read()
        if event == 'Login':
            createdAcc = ReadSettings('LoginMade', JsonPath)
            if createdAcc is True:
                given_name = values['-USERNAME-']
                given_pass = values['-PASSWORD-']
                key = KEY()
                saved_name = ReadSettings('Username', JsonPath)
                saved_pass = savedLogin()
                saved_pass = decryptString(saved_pass).decode()
                if given_name == saved_name and given_pass == saved_pass:
                    window.close()
                    Home(key)
                    sg.popup('Either key is missing or is invalid')

                else:
                    sg.popup('Incorrect login')
            else:
                sg.popup('Please Create Login First')
        if event == 'Create Login':
            login_made = ReadSettings('LoginMade', JsonPath)
            if login_made is True:
                sg.popup('Login Already Created')
            elif login_made is False:
                window.hide()
                CreateLogin()
                window.un_hide()
            else:
                break

        if event == sg.WINDOW_CLOSED:
            sys.exit()

    window.close()
