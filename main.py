#!/usr/bin/env python
import os
import sys
import scripts.ui as Ui
import configparser
from pathlib import Path
from PyQt5.QtWidgets import QApplication
import firebase_admin
from firebase_admin import credentials

def main():
   # Load program settings
   config = configparser.ConfigParser()
   config.read('config\settings.ini')
   
   Path(os.getcwd()+"/temp").mkdir(parents=True, exist_ok=True)
   Path(os.getcwd()+"/out").mkdir(parents=True, exist_ok=True)

   # Init Firebase connection
   try:
      cred = credentials.Certificate(config['fb']['CertificateURL'])
      firebase_admin.initialize_app(cred, {'databaseURL': config['fb']['databaseURL']})
   except:
      print("Can't find Firebase credentials or databaseURL")
   
   # Init PyQt app
   app = QApplication(sys.argv)
   ex = Ui.window()
   ex.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()