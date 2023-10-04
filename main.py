import os, configparser, sys
from utils import *
from psychopass import PsychoPass

if __name__ == "__main__":
    os.system("cls")

    config = configparser.ConfigParser()
    config.read('config.ini')

    verbose = config.getboolean('DEFAULT', 'verbose')

    db_path = os.path.join(os.path.dirname(sys.argv[0]), "psychopass.db")
    PsychoPass(db_path, verbose=verbose)