import PySimpleGUI as sg
import sys
import os
from src.configuration.utils import KEY, ttk_style, list, tmd2, writingTMD
from src.saving import Saving


def loadList():
    try:
        if os.path.getsize(tmd2) > 0:
            data = list(tmd2)
        else:
            data = ''
    except FileNotFoundError:
        data = ''

    return data

def updateMultiline(multiline_element):
    # Generate or retrieve the updated data
    updated_data = loadList()

    # Update the multiline element with the new data
    multiline_element.update(value=updated_data)

def Home(key):
    savedKey = KEY()
    if key == savedKey:
        layout = [[sg.Text('PyschoPass Menu')],
                  [sg.Multiline(size=(80, 20), key='-MULTILINE-')],
                  [sg.Button('Save Passwords'), sg.Button('Options'), sg.Button('Close')]]
        window = sg.Window('PsychoPass', layout, use_ttk_buttons=True, ttk_theme=ttk_style)

        multiline_element = window['-MULTILINE-']

        while True:
            event, values = window.read()
            if event == 'Save Passwords':
                window.hide()
                Saving()
                window.un_hide()
                updateMultiline(multiline_element)  # Update the multiline element with the new data

            if event == 'Close' or event == sg.WINDOW_CLOSED:
                sys.exit()

        window.close()

# Call the Home function with the appropriate key
Home('your_key')
