import PySimpleGUI as sg
import sys
from src.configuration.utils import KEY, encryptString, saveLogin, ttk_style
from src.configuration.jsonManagement import JsonPath, JsonQEdit, JsonQReplace

def CreateLogin():
    if KEY == KEY:
        sg.theme('LightGreen3')

        layout = [
            [sg.Text('PsychoPass Login Creation', size=(24, 1), font=('Helvetica', 20), justification='center')],
            [sg.Text('Username:', size=(12, 1), font=('Helvetica', 12)), 
            sg.Input(key='-USERNAME-', size=(20, 1), font=('Helvetica', 12))],
            [sg.Text('Password:', size=(12, 1), font=('Helvetica', 12)), 
            sg.Input(key='-PASSWORD-', size=(20, 1), font=('Helvetica', 12), password_char='*')],
            [sg.Button('Save Login', size=(10, 1), font=('Helvetica', 12)), 
            sg.Button('Back', size=(10, 1), font=('Helvetica', 12))]
        ]

        window = sg.Window('PsychoPass Login Creation', layout, element_justification='center', margins=(20, 20), use_ttk_buttons=True, ttk_theme=ttk_style)

        while True:
            event, values = window.read()
            if event == 'Save Login':
                key = KEY()
                username = values['-USERNAME-']
                password = values['-PASSWORD-']
                password = encryptString(password, key)
                saveLogin(password)
                JsonQEdit('Username', username)
                JsonQReplace('LoginMade', True)
                sg.popup('Password Saved!')

            if event == 'Back':
                break

            if event == sg.WINDOW_CLOSED:
                sys.exit()

        window.close()

    else:
        sys.exit()