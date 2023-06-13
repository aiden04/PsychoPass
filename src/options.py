import PySimpleGUI as sg
import sys
import os
from src.createLogin import CreateLogin
from src.configuration.jsonManagement import ReadSettings, JsonPath
from src.configuration.utils import tmd1, tmd2, tmd3, decryptString, savedLogin, clearTMD, ttk_style

def verifyLogin():
    layout = [
        [sg.Text('Please Verify Your Login', font=('Helvetica', 20))],
        [sg.Text('Username', font=('Helvetica')), sg.Input(key='-USERNAME-')],
        [sg.Text('Password', font=('Helvetica')), sg.Input(key='-PASSWORD-', password_char='*')],
        [sg.Button('Verify', size=(15, 1), font=('Helvetica')), sg.Button('Back', size=(15, 1), font=('Helvetica'))]
    ]
    window = sg.Window('Verify Login', layout, element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style)

    while True:
        event, values = window.read()

        if event == 'Verify':
            given_name = values['-USERNAME-']
            given_pass = values['-PASSWORD-']
            saved_name = ReadSettings('Username', JsonPath)
            saved_pass = savedLogin()
            saved_pass = decryptString(saved_pass).decode()

            if given_name == saved_name and given_pass == saved_pass:
                clearTMD(tmd2)
                window.hide()
                CreateLogin()
                sg.popup('Login Reset!')
                break
            else:
                sg.popup('Incorrect Login')

        if event == 'Back':
            break

        if event == sg.WIN_CLOSED:
            sys.exit()

    window.close()

def Confirmation():
    layout = [[sg.Text('This will reset all data including login, passwords and encryption key.')],
              [sg.Text('Are you sure you want to continue?')],
              [sg.Button('Yes'), sg.Button('No')]]
    window = sg.Window('Confirm', layout)
    while True:
        event, values = window.read()
        if event == 'Yes':
            os.remove(tmd1)
            os.remove(tmd2)
            os.remove(tmd3)
            os.remove(JsonPath)
            sg.popup('All data reset! PyschoPass will now close')
            sys.exit()
        if event == 'No':
            break
        if event == sg.WIN_CLOSED:
            sys.exit()
    window.close()

def Options():
    layout = [
        [sg.Text('Options', font=('Helvetica', 20))],
        [sg.Button('Reset Login', size=(15, 1), font=('Helvetica')), sg.Button('Reset Data', size=(15, 1), font=('Helvetica')), sg.Button('Back', size=(15, 1), font=('Helvetica'))]
    ]
    window = sg.Window('Options', layout, element_justification='center', use_ttk_buttons=True, ttk_theme=ttk_style)

    while True:
        event, values = window.read()

        if event == 'Reset Login':
            window.hide()
            verifyLogin()
            break
        if event == 'Reset Data':
            Confirmation()
        if event == 'Back':
            break

        if event == sg.WIN_CLOSED:
            sys.exit()

    window.close()