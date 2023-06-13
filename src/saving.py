import PySimpleGUI as sg
import sys
from src.configuration.utils import KEY, encryptString, writingTMD, ttk_style

def Saving():
    Layout = [[sg.Text("Save Passwords Here")],
              [sg.Text('Username'), sg.Input(key='-USERNAME-')],
              [sg.Text('Email'), sg.Input(key='-EMAIL-')],
              [sg.Text('Password'), sg.Input(key='-PASSWORD-')],
              [sg.Text('Website'), sg.Input(key='-WEBSITE-')],
              [sg.Button('Save'), sg.Button('Generate'), sg.Button('Back')]]
    window = sg.Window('Save Passwords Here', Layout, use_ttk_buttons=True, ttk_theme=ttk_style)
    while True:
        event, values = window.read()
        if event == 'Save':
            username = values['-USERNAME-']
            email = values['-EMAIL-']
            password = values['-PASSWORD-']
            website = values['-WEBSITE-']
            writingTMD(email, username, password, website)
        if event == 'Back':
            break
        if event == sg.WIN_CLOSED:
            sys.exit()
    window.close()
        