from src.configuration.jsonManagement import JsonPath, JsonDefault, FirstRunCheck, CheckTDMFiles
from src.configuration.utils import keyCheck
from src.login import Login

FirstRunCheck(JsonDefault, JsonPath)
CheckTDMFiles()
keyCheck()
Login()