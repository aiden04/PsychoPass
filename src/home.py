import PySimpleGUI as sg
import sys
import os
from src.configuration.utils import KEY, ttk_style, list, tmd2, writingTMD, clearTMD
from src.saving import Saving

def Home(key):
    savedKey = KEY()
    if key == savedKey:
        data = list(tmd2)
        layout = [[sg.Text('PyschoPass Menu')],
                  [sg.Multiline(data, size=(80, 20), key='-MULTILINE-')],
                  [sg.Button('Save Passwords'), sg.Button('Options'), sg.Button('Clear Passwords'), sg.Button('Close')]]
        window = sg.Window('PsychoPass', layout, use_ttk_buttons=True, ttk_theme=ttk_style)

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
            if event == 'Close' or event == sg.WINDOW_CLOSED:
                sys.exit()

        window.close()
