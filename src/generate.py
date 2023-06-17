import PySimpleGUI as sg
import sys
from src.configuration.utils import writingTMD, GenPass, ttk_style, icon

def GenDef():
    password = GenPass()


    layout = [
        [sg.Text('Your generated password is', font=('Helvetica', 16))],
        [sg.Text(password, key='-PASSWORD-', font=('Helvetica', 16), justification='center')],
        [sg.Text('If you want to change your password, press "Regenerate" below.', font=('Helvetica', 12))],
        [sg.Text('Please enter information associated with the password below.', font=('Helvetica', 12))],
        [sg.Text('Username', size=(10, 1)), sg.Input(key='-USERNAME-', size=(20, 1))],
        [sg.Text('Email', size=(10, 1)), sg.Input(key='-EMAIL-', size=(20, 1))],
        [sg.Text('Website', size=(10, 1)), sg.Input(key='-WEBSITE-', size=(20, 1))],
        [sg.Button('Save', size=(10, 1)), sg.Button('Regenerate', size=(10, 1)), sg.Button('Back', size=(10, 1))]
    ]

    window = sg.Window('Generated Password', layout, icon=icon, element_justification='center', margins=(10, 10), use_ttk_buttons=True, ttk_theme=ttk_style)

    while True:
        event, values = window.read()
        if event == 'Save':
            username = values['-USERNAME-']
            email = values['-EMAIL-']
            website = values['-WEBSITE-']
            saved = writingTMD(username, email, password, website)
            sg.popup(saved, font=('Helvetica', 12), title='Save Result', icon=icon)
        elif event == 'Back':
            break
        elif event == 'Regenerate':
            password = GenPass()
            window['-PASSWORD-'].update(password)
        elif event == sg.WIN_CLOSED:
            sys.exit()

    window.close()
