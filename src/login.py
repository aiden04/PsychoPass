import PySimpleGUI as sg
import sys
import tempfile
from src.createLogin import CreateLogin
from src.configuration.jsonManagement import ReadSettings, JsonPath
from src.configuration.utils import encryptString, decryptString, KEY, savedLogin

def Login():
    Layout = [[sg.Text('PsychoPass Login')],
              [sg.Text('Username'), sg.Input(key='-USERNAME-')],
              [sg.Text('Password'), sg.Input(key='-PASSWORD-')],
              [sg.Button('Login'), sg.Button('Create Login')]]
    Window = sg.Window('PsychoPass Login', Layout)
    while True:
        event, values = Window.Read()
        if event == 'Login':
            key = KEY()
            GivenName = values['-USERNAME-']
            SavedName = ReadSettings('Username', JsonPath)
            GivenPass = values['-PASSWORD-']
            SavedPass = savedLogin()
            SavedPass = decryptString(SavedPass, key)
            if GivenPass == SavedPass:
                break
            else:
                sg.popup('Incorrect Login')
        if event == "Create Login":
            LoginMade = ReadSettings('LoginMade', JsonPath)
            if LoginMade is True:
                sg.popup('Login Already Created')
            elif LoginMade is False:
                Window.hide()
                CreateLogin()
                Window.un_hide()
            else:
                break
        if event == sg.WIN_CLOSED:
            sys.exit()
    Window.close()