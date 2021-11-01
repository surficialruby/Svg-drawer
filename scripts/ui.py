import configparser
from PyQt5.QtCore import QRect, pyqtSignal
from PyQt5.QtGui import QMoveEvent
from PyQt5.QtWidgets import QFrame, QGraphicsOpacityEffect, QLineEdit, QPushButton, QMainWindow, QAction, QFileDialog, QTextEdit, QWidget
from scripts import (
    canvas, 
    save, 
    objectController as oc,
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
      newAction.triggered.connect(lambda:self.showNPW())

      # Create new action
      openAction = QAction('&Open', self)        
      openAction.setShortcut('Ctrl+O')
      openAction.setStatusTip('Open document')
      #openAction.triggered.connect()

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
      self.layout.setGeometry(QRect(0, 20, 50, self.frameGeometry().height()))

      #Add new preset img
      self.add_btn = QPushButton('Add',self.layout)
      self.add_btn.resize(50,40)
      self.add_btn.clicked.connect(lambda:self.add_preset('preset_checkbox.svg'))
      
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

      #Load background
      self.bg = canvas.Background(self.canvas,'bg.svg')
      oc.addBG(self.bg)

   def showNPW(self):
      self.modal = QFrame(self)
      self.modal.resize(int(self.settings['display']['width']),int(self.settings['display']['height']))

      self.overlay = QFrame(self.modal)
      self.overlay.resize(int(self.settings['display']['width']),int(self.settings['display']['height']))
      self.overlay.move(0,20)
      self.overlay.setStyleSheet('background-color:#36373d;') 
      self.opacity_effect = QGraphicsOpacityEffect()
      self.opacity_effect.setOpacity(0.3)
      self.overlay.setGraphicsEffect(self.opacity_effect)

      self.front = QFrame(self.modal)
      self.front.resize(300,480)
      self.front.move(int(self.settings['display']['width'])/2-self.front.frameGeometry().width()/2,int(self.settings['display']['height'])/2-self.front.frameGeometry().height()/2)
      self.front.setStyleSheet('background-color:white;') 

      frontCenter = self.front.frameGeometry().width()/2
      self.bgName = QTextEdit(self.front)
      self.bgName.setReadOnly(True)
      self.bgName.move(frontCenter-self.bgName.frameGeometry().width()/2,20)

      self.bgSelect = QPushButton('select',self.front)
      self.bgSelect.resize(50,40)
      self.bgSelect.clicked.connect(lambda:self.openFileNameDialog())
      self.bgSelect.move(frontCenter-self.bgSelect.frameGeometry().width()/2,20)

      self.cbName = QLineEdit(self.front)
      self.cbName.setReadOnly(True)
      self.cbName.move(frontCenter-self.cbName.frameGeometry().width()/2,20)

      self.cbSelect = QPushButton('select',self.front)
      self.cbSelect.resize(50,40)
      self.cbSelect.clicked.connect(lambda:self.openFileNameDialog())
      self.cbSelect.move(frontCenter-self.cbSelect.frameGeometry().width()/2,20)

      self.okBtn = QPushButton('Ok',self.front)
      self.okBtn.resize(50,40)
      self.okBtn.clicked.connect(lambda:self.modal.close())
      self.okBtn.move(frontCenter-self.okBtn.frameGeometry().width()/2,20)

      self.cancelBtn = QPushButton('Cancel',self.front)
      self.cancelBtn.resize(50,40)
      self.cancelBtn.clicked.connect(lambda:self.modal.close())
      self.cancelBtn.move(frontCenter-self.cancelBtn.frameGeometry().width()/2,20)

      self.modal.show()
   
   def openFileNameDialog(self):
      options = QFileDialog.Options()
      options |= QFileDialog.DontUseNativeDialog
      fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","SVG Files (*.svg);;All Files (*)", options=options)
      if fileName:
         print(fileName)

   def resizeEvent(self, event):
      self.resized.emit()
      return super(window, self).resizeEvent(event)

   def resizeCanvas(self):
      self.canvas.resize(self.frameGeometry().width()-50,self.frameGeometry().height()-20)
      self.bg.origPos()

   def add_preset(self,preset):
      oc.deselectAll()
      oc.add(canvas.PresetImg(oc.bg,preset))

   def save(self):
      save.save()

   def mousePressEvent(self, event: QMoveEvent):
      # Deselect selected checkbox elements
      oc.deselectAll()

class NewProjectWindow(QWidget):
   switch_window = pyqtSignal()

   def __init__(self, parent=None):
      super(NewProjectWindow, self).__init__(parent)
      self.width = 300
      self.height = 480
      self.initUI()
   
   def initUI(self):
      self.setWindowTitle(self.title)
      self.resize(self.width, self.height)

      self.bg = QPushButton('select', self)
      self.bg.resize(50,40)
      self.bg.move(0,45)
      self.bg.clicked.connect(lambda:self.openFileNameDialog())

      self.cb = QPushButton('select', self)
      self.cb.resize(50,40)
      self.cb.move(0,45)
      self.cb.clicked.connect(lambda:self.openFileNameDialog())

      #self.openFileNameDialog()

   def openFileNameDialog(self):
      options = QFileDialog.Options()
      options |= QFileDialog.DontUseNativeDialog
      fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","SVG Files (*.svg);;All Files (*)", options=options)
      if fileName:
         print(fileName)


