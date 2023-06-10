import PySimpleGUI as sg
import json
import sys
from src.configuration.utils import KEY, encryptString, saveLogin
from src.configuration.jsonManagement import JsonPath, JsonQEdit, JsonQReplace

def CreateLogin():
    Layout = [[sg.Text('PyschoPass Login Creation')],
              [sg.Text('Username'), sg.Input(key='-USERNAME-')],
              [sg.Text('Password'), sg.Input(key='-PASSWORD-')],
              [sg.Button('Save Login'), sg.Button('Back')]]
    Window = sg.Window('PsychoPass Login Creation', Layout)
    while True:
        event, values = Window.Read()
        if event == 'Save Login':
            key = KEY()
            Username = values['-USERNAME-']
            Password = values['-PASSWORD-']
            Password = encryptString(Password, key)
            saveLogin(Password)
            JsonQEdit('Username', Username)
            JsonQReplace('LoginMade', True)
            
            sg.popup('Password Saved!')

        if event == 'Back':
            break
        if event == sg.WIN_CLOSED:
            sys.exit()
    Window.close()