import sys
import requests
from PyQt5.QtWidgets import *
import configparser as cp
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the config file
filename = os.path.join(os.path.dirname(script_dir), 'config.ini')

inifile = cp.ConfigParser()
try:
    # Use utf-8 encoding and check if file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Configuration file not found: {filename}")
    
    inifile.read(filename, encoding='utf-8')
    
    # Verify sections exist before accessing
    if not inifile.has_section('server'):
        raise cp.NoSectionError('server')
    
    App = QApplication(sys.argv)

    try:
        response = requests.get('http://{}:{}/api/connect'.format(
            inifile.get("server","ip"),
            inifile.get("server","port")
        ), timeout=5)
        print(response.text)

    except Exception as e:
        QMessageBox.critical(None, "Status", "Fail to connect to CSC server \nPlease check again")
        print(e)
        sys.exit("Fail to start application")

except (cp.NoSectionError, FileNotFoundError) as config_error:
    QMessageBox.critical(None, "Configuration Error", 
                         f"Configuration error: {config_error}\n"
                         f"Please check your config.ini file at {filename}")
    sys.exit(1)