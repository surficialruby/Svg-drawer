#!/usr/bin/env python
import sys
import scripts.ui as Ui
import configparser
from PyQt5.QtWidgets import QApplication
import firebase_admin
from firebase_admin import credentials

def main():
   # Load program settings
   config = configparser.ConfigParser()
   config.read('config\settings.ini')
   # Init Firebase connection
   cred = credentials.Certificate(config['fb']['sdkURL'])
   firebase_admin.initialize_app(cred, {'databaseURL': config['fb']['databaseURL']})
   
   # Init PyQt app
   app = QApplication(sys.argv)
   ex = Ui.window()
   ex.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()