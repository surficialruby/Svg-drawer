import configparser
import json
import firebase_admin
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QLineEdit, QListWidget, QPushButton, QMainWindow, QAction, QFileDialog
from firebase_admin.db import Event
from scripts import (
    canvas, 
    save, 
    objectController as oc,
    Firebase as fb,
)

class window(QMainWindow):
   resized = pyqtSignal()

   def __init__(self, parent = None):
      super(window, self).__init__(parent)
      # Load program settings
      self.settings = configparser.ConfigParser()
      self.settings.read('config\settings.ini')
      self.initUI()

   def initUI(self):
      self.resize(int(self.settings['display']['width']),int(self.settings['display']['height']))
      self.setWindowTitle('SVG drawer')
      self.initMenu()
      self.initBtns()
      self.initCanvas()
      self.resized.connect(self.resizeCanvas)

   def initMenu(self):
      # Create new action
      newAction = QAction('&New', self)        
      newAction.setShortcut('Ctrl+N')
      newAction.setStatusTip('New document')
      newAction.triggered.connect(lambda:self.showNPM())

      # Create new action
      openAction = QAction('&Open', self)        
      openAction.setShortcut('Ctrl+O')
      openAction.setStatusTip('Open document')
      openAction.triggered.connect(lambda:self.showLPM())

      # Create exit action
      exitAction = QAction('&save', self)        
      exitAction.setShortcut('Ctrl+S')
      exitAction.setStatusTip('save')
      exitAction.triggered.connect(self.save)

      # Create menu bar and add actions
      menuBar = self.menuBar()
      fileMenu = menuBar.addMenu('&File')
      fileMenu.addAction(newAction)
      fileMenu.addAction(openAction)
      fileMenu.addAction(exitAction)

   def initBtns(self):
      #Btn holder
      self.layout = QFrame(self)
      self.layout.setGeometry(0, 20, 50, self.frameGeometry().height())

      #Add new preset img
      self.add_btn = QPushButton('Add',self.layout)
      self.add_btn.resize(50,40)
      self.add_btn.clicked.connect(lambda:self.add_preset())
      
      '''
      #Edit selector
      self.edit_btn = QPushButton('Edit',self.layout)
      self.edit_btn.resize(50,40)
      self.edit_btn.move(0,45)
      # TEMP SAVE FOR EDIT BUTTON
      self.edit_btn.clicked.connect()
      
      #Delete selected
      self.del_btn = QPushButton('Del',self.layout)
      self.del_btn.resize(50,40)
      self.del_btn.move(0,90)

      #Edit text
      self.edit_btn = QPushButton('Text',self.layout)
      self.edit_btn.resize(50,40)
      self.edit_btn.move(0,135)
      self.edit_btn.clicked.connect(lambda:self.deselectAll())
      '''

   def initCanvas(self):
      #canvas
      self.canvas = QFrame(self)
      self.canvas.move(50,20)
      self.canvas.resize(self.frameGeometry().width()-50,self.frameGeometry().height()-20)
      self.canvas.setStyleSheet('border: 1px solid black;')

      #Load empty background
      self.bg = canvas.Background(self.canvas)
      oc.addBG(self.bg)

   def initNewProject(self):
      if self.bgName.text() != '' and self.cbName.text() != '' and self.projectName.text() != '':
         oc.updateID('')

         # Load background
         self.bg = canvas.Background(self.canvas,self.bgName.text())
         oc.addBG(self.bg)
         self.bg.show()
         # Add preset location
         oc.addPreset(self.cbName.text())
         
         self.settings['save']['url'] = self.imgURL.text()
         self.settings['save']['name'] = self.projectName.text()
         with open('config/settings.ini', 'w') as configfile:    # save
            self.settings.write(configfile)

         self.modalNPM.close()

   def initLoadedProject(self):
      if self.bgName.text() != '':
         if self.listwidget.currentItem():
            selectedProject = self.projects[self.listwidget.currentItem().text()]
            loadedKey = ''
            for key in self.maps:
               if self.listwidget.currentItem().text() == self.maps[key]['MAP']['name']:
                  loadedKey = key
            oc.updateID(loadedKey)
         elif self.localJSON:
            with open(self.localJSON.text()) as json_file:
               selectedProject = json.load(json_file)

         # Add preset location
         oc.addPreset(self.cbName.text())
         # Load background
         self.bg = canvas.Background(self.canvas,self.bgName.text())
         oc.addBG(self.bg)
         self.bg.show()
         self.bg.addChilds()
         
         self.settings['save']['url'] = selectedProject['URL']
         self.settings['save']['name'] = selectedProject['MAP']['name']
         with open('config/settings.ini', 'w') as configfile:    # save
            self.settings.write(configfile)

         self.modalLPM.close()

   def showNPM(self):
      self.modalNPM = QFrame(self)
      self.modalNPM.resize(int(self.settings['display']['width']),int(self.settings['display']['height']))

      self.overlay = QFrame(self.modalNPM)
      self.overlay.resize(int(self.settings['display']['width']),int(self.settings['display']['height']))
      self.overlay.move(0,20)
      self.overlay.setStyleSheet('background-color:#36373d;') 
      self.opacity_effect = QGraphicsOpacityEffect()
      self.opacity_effect.setOpacity(0.3)
      self.overlay.setGraphicsEffect(self.opacity_effect)

      self.front = QFrame(self.modalNPM)
      self.front.resize(300,480)
      self.front.move(round(int(self.settings['display']['width'])/2-self.front.frameGeometry().width()/2),round(int(self.settings['display']['height'])/2-self.front.frameGeometry().height()/2))
      self.front.setStyleSheet('background-color:white;') 

      frontCenterW = self.front.frameGeometry().width()/2

      self.projectNameLabel = QLabel(self.front)
      self.projectNameLabel.setText('Project name')
      self.projectNameLabel.move(round(frontCenterW-self.projectNameLabel.frameGeometry().width()/2)-35,30)
      self.projectName = QLineEdit(self.front)
      self.projectName.move(round(frontCenterW-self.projectName.frameGeometry().width()/2)-35,50)

      self.bgNameLabel = QLabel(self.front)
      self.bgNameLabel.setText('Background')
      self.bgNameLabel.move(round(frontCenterW-self.bgNameLabel.frameGeometry().width()/2)-35,80)
      self.bgName = QLineEdit(self.front)
      self.bgName.setReadOnly(True)
      self.bgName.move(round(frontCenterW-self.bgName.frameGeometry().width()/2)-35,100)
      self.bgSelect = QPushButton('browse',self.front)
      self.bgSelect.resize(50,20)
      self.bgSelect.move(round(frontCenterW-self.bgSelect.frameGeometry().width()/2)+75,100)
      self.bgSelect.clicked.connect(lambda:self.bgName.setText(self.openfilenameDialog()))

      self.cbNameLabel = QLabel(self.front)
      self.cbNameLabel.setText('Checkbox preset')
      self.cbNameLabel.move(round(frontCenterW-self.cbNameLabel.frameGeometry().width()/2)-35,130)
      self.cbName = QLineEdit(self.front)
      self.cbName.setReadOnly(True)
      self.cbName.move(round(frontCenterW-self.cbName.frameGeometry().width()/2)-35,150)
      self.cbSelect = QPushButton('browse',self.front)
      self.cbSelect.resize(50,20)
      self.cbSelect.move(round(frontCenterW-self.cbSelect.frameGeometry().width()/2)+75,150)
      self.cbSelect.clicked.connect(lambda:self.cbName.setText(self.openfilenameDialog()))

      self.imgUrlLabel = QLabel(self.front)
      self.imgUrlLabel.setText('Image url')
      self.imgUrlLabel.move(round(frontCenterW-self.projectNameLabel.frameGeometry().width()/2)-35,180)
      self.imgURL = QLineEdit(self.front)
      self.imgURL.move(round(frontCenterW-self.projectName.frameGeometry().width()/2)-35,200)

      self.okBtn = QPushButton('Ok',self.front)
      self.okBtn.resize(50,40)
      self.okBtn.clicked.connect(lambda:self.initNewProject())
      self.okBtn.move(round(frontCenterW-self.okBtn.frameGeometry().width()/2)-50,round(self.front.frameGeometry().height()-self.okBtn.frameGeometry().height())-20)

      self.cancelBtn = QPushButton('Cancel',self.front)
      self.cancelBtn.resize(50,40)
      self.cancelBtn.clicked.connect(lambda:self.modalNPM.close())
      self.cancelBtn.move(round(frontCenterW-self.cancelBtn.frameGeometry().width()/2)+50,round(self.front.frameGeometry().height()-self.cancelBtn.frameGeometry().height())-20)

      self.modalNPM.show()

   def showLPM(self):
      self.modalLPM = QFrame(self)
      self.modalLPM.resize(int(self.settings['display']['width']),int(self.settings['display']['height']))

      self.overlay = QFrame(self.modalLPM)
      self.overlay.resize(int(self.settings['display']['width']),int(self.settings['display']['height']))
      self.overlay.move(0,20)
      self.overlay.setStyleSheet('background-color:#36373d;') 
      self.opacity_effect = QGraphicsOpacityEffect()
      self.opacity_effect.setOpacity(0.3)
      self.overlay.setGraphicsEffect(self.opacity_effect)

      self.front = QFrame(self.modalLPM)
      self.front.resize(300,480)
      self.front.move(round(int(self.settings['display']['width'])/2-self.front.frameGeometry().width()/2),round(int(self.settings['display']['height'])/2-self.front.frameGeometry().height()/2))
      self.front.setStyleSheet('background-color:white;') 

      frontCenterW = self.front.frameGeometry().width()/2

      self.mapJsonLabel = QLabel(self.front)
      self.mapJsonLabel.setText('Firebase Map json')
      self.mapJsonLabel.move(round(frontCenterW-self.mapJsonLabel.frameGeometry().width()/2)-35,20)
      self.listwidget = QListWidget(self.front)
      self.listwidget.resize(200,150)
      self.listwidget.move(round(frontCenterW-self.listwidget.frameGeometry().width()/2)+10,40)

      if firebase_admin._apps:
         self.maps = fb.fbGetMaps()
         self.projects = {}
         if self.maps:
            for idx, map in enumerate(self.maps):
               self.projects[self.maps[map]['MAP']['name']] = self.maps[map]
               self.listwidget.insertItem(idx, self.maps[map]['MAP']['name'])

      self.jsonNameLabel = QLabel(self.front)
      self.jsonNameLabel.setText('Local map json')
      self.jsonNameLabel.move(round(frontCenterW-self.jsonNameLabel.frameGeometry().width()/2)-35,200)
      self.localJSON = QLineEdit(self.front)
      self.localJSON.setReadOnly(True)
      self.localJSON.move(round(frontCenterW-self.localJSON.frameGeometry().width()/2)-35,220)
      self.jsonSelect = QPushButton('browse',self.front)
      self.jsonSelect.resize(50,20)
      self.jsonSelect.move(round(frontCenterW-self.jsonSelect.frameGeometry().width()/2)+75,220)
      self.jsonSelect.clicked.connect(lambda:self.localJSON.setText(self.openJSONDialog()))

      self.bgNameLabel = QLabel(self.front)
      self.bgNameLabel.setText('SVG image')
      self.bgNameLabel.move(round(frontCenterW-self.bgNameLabel.frameGeometry().width()/2)-35,250)
      self.bgName = QLineEdit(self.front)
      self.bgName.setReadOnly(True)
      self.bgName.move(round(frontCenterW-self.bgName.frameGeometry().width()/2)-35,270)
      self.bgSelect = QPushButton('browse',self.front)
      self.bgSelect.resize(50,20)
      self.bgSelect.move(round(frontCenterW-self.bgSelect.frameGeometry().width()/2)+75,270)
      self.bgSelect.clicked.connect(lambda:self.bgName.setText(self.openfilenameDialog()))

      self.cbNameLabel = QLabel(self.front)
      self.cbNameLabel.setText('Checkbox preset')
      self.cbNameLabel.move(round(frontCenterW-self.cbNameLabel.frameGeometry().width()/2)-35,300)
      self.cbName = QLineEdit(self.front)
      self.cbName.setReadOnly(True)
      self.cbName.move(round(frontCenterW-self.cbName.frameGeometry().width()/2)-35,320)
      self.cbSelect = QPushButton('browse',self.front)
      self.cbSelect.resize(50,20)
      self.cbSelect.move(round(frontCenterW-self.cbSelect.frameGeometry().width()/2)+75,320)
      self.cbSelect.clicked.connect(lambda:self.cbName.setText(self.openfilenameDialog()))

      self.okBtn = QPushButton('Ok',self.front)
      self.okBtn.resize(50,40)
      self.okBtn.clicked.connect(lambda:self.initLoadedProject())
      self.okBtn.move(round(frontCenterW-self.okBtn.frameGeometry().width()/2)-50,round(self.front.frameGeometry().height()-self.okBtn.frameGeometry().height())-20)

      self.cancelBtn = QPushButton('Cancel',self.front)
      self.cancelBtn.resize(50,40)
      self.cancelBtn.clicked.connect(lambda:self.modalLPM.close())
      self.cancelBtn.move(round(frontCenterW-self.cancelBtn.frameGeometry().width()/2)+50,round(self.front.frameGeometry().height()-self.cancelBtn.frameGeometry().height())-20)

      self.modalLPM.show()

   def openfilenameDialog(self):
      options = QFileDialog.Options()
      options |= QFileDialog.DontUseNativeDialog
      filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","SVG Files (*.svg);;All Files (*)", options=options)
      if filename:
         return filename
      
   def openJSONDialog(self):
      options = QFileDialog.Options()
      options |= QFileDialog.DontUseNativeDialog
      filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","JSON Files (*.json);;All Files (*)", options=options)
      if filename:
         return filename

   def resizeEvent(self, event) -> Event:
      self.resized.emit()
      return super(window, self).resizeEvent(event)

   def resizeCanvas(self):
      self.canvas.resize(self.frameGeometry().width()-50,self.frameGeometry().height()-20)
      self.bg.origPos()

   def add_preset(self):
      if oc.preset != '':
         oc.deselectAll()
         oc.add(canvas.PresetImg(oc.bg,oc.preset))

   def save(self):
      if oc.bg.filename != None:
         save.save()

   def mousePressEvent(self, event):
      # Deselect selected checkbox elements
      oc.deselectAll()
