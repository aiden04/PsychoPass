import PySimpleGUI as sg
import sys
from src.configuration.utils import writingTMD, ttk_style, icon
from src.generate import GenDef

def Saving():

    layout = [
        [sg.Text("Save Passwords Here", font=('Helvetica', 16), justification='center')],
        [sg.Text('Username', size=(12, 1)), sg.Input(key='-USERNAME-', size=(20, 1))],
        [sg.Text('Email', size=(12, 1)), sg.Input(key='-EMAIL-', size=(20, 1))],
        [sg.Text('Password', size=(12, 1)), sg.Input(key='-PASSWORD-', size=(20, 1))],
        [sg.Text('Website', size=(12, 1)), sg.Input(key='-WEBSITE-', size=(20, 1))],
        [sg.Button('Save', size=(10, 1)), sg.Button('Generate', size=(10, 1)), sg.Button('Back', size=(10, 1))]
    ]

    window = sg.Window('Save Passwords', layout, icon=icon, element_justification='center', margins=(10, 10), use_ttk_buttons=True, ttk_theme=ttk_style)

    while True:
        event, values = window.read()
        if event == 'Save':
            username = values['-USERNAME-']
            email = values['-EMAIL-']
            password = values['-PASSWORD-']
            website = values['-WEBSITE-']
            saved = writingTMD(email, username, password, website)
            sg.popup(saved, font=('Helvetica', 12), title='Save Result', icon=icon)
        elif event == 'Generate':
            window.hide()
            GenDef()
            window.un_hide()
        elif event == 'Back':
            break
        elif event == sg.WIN_CLOSED:
            sys.exit()

    window.close()
