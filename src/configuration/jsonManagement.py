import json
import os


JsonPath = './src/settings.json'
JsonDefault = {
    'LoginMade': False,
    'Key': False,
    'Username': ''
}

def SearchJsonFile(JsonPath, String):
    with open(JsonPath) as JsonFile:
        data = json.load(JsonFile)
        FoundItems = []

        def RecursiveSearching(data, String, CurrentPath=''):
            if isinstance(data, dict):
                for key, value in data.items():
                    NewPath = CurrentPath + '.' + key if CurrentPath else key
                    if isinstance(value, str) and String in value:
                        FoundItems.append((NewPath, value))
                    elif isinstance(value, (dict, list)):
                        RecursiveSearching(value, String, CurrentPath=NewPath)

            elif isinstance(data, list):
                for index, item in enumerate(data):
                    NewPath = CurrentPath + f'[{index}]'
                    if isinstance(item, str) and String in item:
                        FoundItems.append((NewPath, item))
            elif isinstance(item, (dict, list)):
                RecursiveSearching(item, String, CurrentPath=NewPath)
    RecursiveSearching(data, String)
    return FoundItems

def FirstRunCheck(data, path):
    if not os.path.exists(path):
        with open(path, 'w') as JsonFile:
            json.dump(data, JsonFile)

def ReadSettings(object, path):
    with open(path) as JsonFile:
        data = json.load(JsonFile)
        Object = data.get(object)
        return Object

def CheckTDMFiles():
    tmd1 = 'src/configuration/TMD1'
    tmd2 = 'src/configuration/TMD2'
    tmd3 = 'src/configuration/TMD3'

    tmd1Present = os.path.isfile(tmd1)
    tmd2Present = os.path.isfile(tmd2)
    tmd3Present = os.path.isfile(tmd3)

    if not tmd1Present:
        with open(tmd1, 'w') as file:
            file.write('')
    if not tmd2Present:
        with open(tmd2, 'w') as file:
            file.write('')
    if not tmd3Present:
        with open(tmd3, 'w') as file:
            file.write('')

def JsonQEdit(Value, Content):
    data = {}
    with open(JsonPath, 'r') as JsonFile:
        data = json.load(JsonFile)    
    data[Value] = Content
    with open(JsonPath, 'w') as JsonFile:
        json.dump(data, JsonFile, indent=4)

def JsonQReplace(Value, Content):
    with open(JsonPath, 'r') as JsonFile:
        data = json.load(JsonFile)
    data[Value] = Content
    with open(JsonPath, 'w') as JsonFile:
        json.dump(data, JsonFile, indent=4)
