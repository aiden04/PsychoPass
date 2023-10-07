import os, configparser, sys
from utils import *
from psychopass import PsychoPass

if __name__ == "__main__":
    os.system("cls")

    if os.path.isfile("config.ini") is False:
        print("No config.ini file found. Creating one. . .")
        config = configparser.ConfigParser()
        config['DEBUG'] = {'verbose': 'False'}
        config['DEFAULT'] = {'db_path': 'psychopass.db'}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print("config.ini file created. Please edit it to your liking.")

    config = configparser.ConfigParser()
    config.read('config.ini')

    verbose = config.getboolean('DEBUG', 'verbose')
    db_path = config.get("DEFAULT", "db_path", fallback="psychopass.db")
    if db_path == "psychopass.db":
        if verbose is True: print("Using database at: ", db_path)
        db_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "psychopass.db"))
    else:
        if verbose is True: print("Using database at: ", db_path)
        pass
    PsychoPass(db_path, verbose=verbose)
