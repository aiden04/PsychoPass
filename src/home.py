import PySimpleGUI as sg
import sys
import os
from src.options import Options
from src.configuration.utils import KEY, ttk_style, list, tmd2, writingTMD, clearTMD
from src.saving import Saving

def Home(key):
    savedKey = KEY()
    if key == savedKey:
        data = list(tmd2)
        layout = [
            [sg.Text('PyschoPass Menu', font=('Helvetica', 16, 'bold'))],
            [sg.Multiline(data, size=(55, 15), key='-MULTILINE-', disabled=True, autoscroll=True, font=('Helvetica', 12))],
            [sg.Button('Save Passwords', size=(15, 1)), sg.Button('Options', size=(15, 1)), sg.Button('Clear Passwords', size=(15, 1)), sg.Button('Close', size=(15, 1))]
        ]
        window = sg.Window('PsychoPass', layout, margins=(20, 20), use_ttk_buttons=True, ttk_theme=ttk_style, finalize=True)

        while True:
            event, values = window.read()
            if event == 'Save Passwords':
                window.hide()
                Saving()
                window.un_hide()
                data = list(tmd2)
                window['-MULTILINE-'].update(data)
            if event == 'Clear Passwords':
                Output = clearTMD(tmd2)
                sg.popup(Output)
                data = ''
                window['-MULTILINE-'].update(data)
            if event == 'Options':
                window.hide()
                Options()
                window.un_hide()
            if event == 'Close' or event == sg.WINDOW_CLOSED:
                sys.exit()

        window.close()