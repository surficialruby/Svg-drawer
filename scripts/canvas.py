import os
import cairo
import math
import re
import xml.etree.ElementTree as ET
from svgutils import transform
from PyQt5.QtWidgets import QLabel, QPushButton, QTextEdit
from PyQt5.QtGui import QPixmap, QMouseEvent
from PyQt5.QtCore import Qt, QTimer
from . import objectController as oc
from . import canvas

class Background(QLabel):
    filename = ''
    orig_pos = {'x':0,'y':0}
    move_orig_pos = {'x':0,'y':0}
    svg = ET.ElementTree
    c = {}

    def __init__(self, parent, pixmap = None):
        super().__init__(parent)
        self._parent = parent
        self.filename = pixmap
        if pixmap: self.svg = ET.parse(pixmap)
        if self.filename: self.separateCB()
        pixmap = QPixmap(pixmap)
        self.setPixmap(pixmap)
        self.resize(pixmap.width(),pixmap.height())
        self.origPos()
    
    def origPos(self):
        self.orig_pos = {
            'x':int(self._parent.frameGeometry().width()/2-self.frameGeometry().width()/2),
            'y':int(self._parent.frameGeometry().height()/2-self.frameGeometry().height()/2)
            }
        self.move(self.orig_pos['x'],self.orig_pos['y'])

    def convert(self):
        svg = self.svg.getroot()
        string = ET.tostring(svg)
        return QPixmap.loadFromData(string)

    # Seperate checkboxes from background if there is any. Most likely needs optimization
    def separateCB(self):
        svg = self.svg.getroot()
        svgTxt = ET.tostring(svg).decode()
        svgTxt = svgTxt.replace('ns0:', '')
        svgTxt = svgTxt.replace('<g/>', '')
        svg = ET.ElementTree(ET.fromstring(svgTxt))
        svg = self.svg.getroot()
        checkboxes = re.findall(r'(checkbox_\w+)',svgTxt)
        self.c = {}
        child = ET.ElementTree
        for idx, checkbox in enumerate(checkboxes):
            child = svg.find(f'''.//*[@id='{checkbox}']...''')
            coords = re.findall(r'[0-9]+,\s[0-9]+', child.get('transform'))[0].split(',')
            txt = child.find('''.//*[@id='text']''').text
            svgchild = svg.find(f'''.//*[@id='{checkbox}']''')
            svgStr = ET.tostring(svg).decode()
            childStr = ET.tostring(child).decode()
            childStr = childStr.replace('ns0:', '')
            childStr = childStr.replace('xmlns:ns0="http://www.w3.org/2000/svg" ', '')
            svgStr = svgStr.replace('ns0:', '')
            svgStr = svgStr.replace(childStr, '')
            svg = ET.ElementTree(ET.fromstring(svgStr))
            svg = svg.getroot()
            self.c[checkbox] = svgchild, coords, txt
        svgFigure = transform.fromstring(ET.tostring(svg).decode())
        svgFigure.save('temp/bg.svg','utf-8')
        pixmap = QPixmap('temp/bg.svg')
        self.setPixmap(pixmap)
        self.svg = ET.ElementTree(svg)
        os.remove("temp/bg.svg")
    
    # Adds seperated checkboxes
    def addChilds(self):
        for c in self.c:
            oc.add(canvas.PresetImg(oc.bg,oc.preset,self.c[c][1],self.c[c][2]))
        self.updateBG()

    def updateBG(self):
        svg = self.svg.getroot()
        svg = transform.fromstring(ET.tostring(svg).decode())
        svg.save('temp/bg.svg','utf-8')
        pixmap = QPixmap('temp/bg.svg')
        self.setPixmap(pixmap)
        os.remove("temp/bg.svg")

class PresetImg(QLabel):
    selected = False
    filename = ''
    parentEle = None
    orig_pos = {'x':0,'y':0}
    click_pos = {'x':0,'y':0}
    textSelected = False
    firstrelease = False
    svg = ET.parse
    textAreaHeight = '45'
    timer = QTimer()

    def __init__(self, parent, pixmap = None, coords = None, txt = None):
        super().__init__(parent)
        self.setStyleSheet('border: none;')
        self.filename = pixmap
        self.svg = ET.parse(pixmap)
        self.parentEle = parent
        pixmap = QPixmap(pixmap)
        self.setPixmap(pixmap)
        self.resize(pixmap.width(),pixmap.height())
        if not coords:
            self.orig_pos = {
                'x':int(parent.frameGeometry().width()/2-self.frameGeometry().width()/2),
                'y':int(parent.frameGeometry().height()/2-self.frameGeometry().width()/2)
                }
        else:
            self.orig_pos = {
                'x':int(coords[0]),
                'y':int(coords[1])
                }
        self.move(self.orig_pos['x'],self.orig_pos['y'])
        if txt:
            self.updateText(txt)

    def delete(self):
        oc.delete(self)
        self.setParent(None)
        self.deleteLater()

    def timerStopped(self):
        self.timer.stop()

    def checkDoubleClick(self):
        if self.timer.isActive():
            self.textEditor()
            self.timer.stop()

    def select(self):
        oc.deselectAll()
        self.selected = True
        self.setStyleSheet('border: 1px solid red;')

    def deselect(self):
        self.selected = False
        self.setStyleSheet('border: none;')
        if hasattr(self,'textEdit'):
            self.textEdit.setParent(None)
            self.textEdit.deleteLater()
            delattr(self,'textEdit')
        if hasattr(self,'rcMenu'):
            self.rcMenu.setParent(None)
            self.rcMenu.deleteLater()
            delattr(self,'rcMenu')
        
    def textEditor(self):
        self.textSelected = True
        x = round(float(self.svg.getroot()[0][2][0].get('x')))
        y = 5
        width = round(float(self.svg.getroot()[0][2][0].get('width')))
        height = round(float(self.svg.getroot()[0][2][0].get('height')))
        if not hasattr(self,'textEdit'):
            self.textEdit = QTextEdit(self)
            self.textEdit.move(x,y)
            self.textEdit.resize(width*2+2,height*2)
            self.textEdit.setPlainText(self.svg.getroot()[0][2][1].text)
            self.textEdit.show()
            self.textEdit.setFocus()

    # Get textarea plain text and split it to rows to fit checkbox width
    def saveText(self):
        if hasattr(self, 'textEdit'):
            fontSize = 7.8
            self.svg.getroot()[0][2][1].text = self.textEdit.toPlainText()
            plainText = self.textEdit.toPlainText().splitlines()
            svgTextArr = []
            width = float(self.svg.getroot()[0][2][0].get('width'))
            for idx, line in enumerate(plainText):
                if self.textwidth(line, fontSize) > width:
                    words = line.split(' ')
                    newLine = []
                    tempLine = ''
                    i = 0
                    for word in words:
                        if self.textwidth(tempLine + ' ' + word, fontSize) <= width:
                            tempLine += ' ' + word
                        else:
                            i+=1
                            if len(tempLine) > 0: 
                                newLine.append(tempLine)
                            for i in range(math.ceil(self.textwidth(word, fontSize)/width)):
                                tempLine = ''
                                i+=1
                                if len(word) > 0:
                                    splitWord = word[0:math.floor(width/(self.textwidth(word, fontSize) / len(word)))]
                                    if len(newLine) > 0: 
                                        lineLen = self.textwidth(newLine[len(newLine)-1] + ' ' + splitWord, fontSize)
                                    if len(newLine) > 0 and lineLen <= width: 
                                        newLine[len(newLine)-1] + ' ' + splitWord
                                    else:
                                        newLine.append(word[0:math.floor(width/(self.textwidth(word, fontSize) / len(word)))])
                                    word = word[math.floor(width/(self.textwidth(word, fontSize) / len(word)))+1:]
                                i+=1
                    if len(tempLine) > 0: 
                        newLine.append(tempLine)
                    for line_ in newLine:
                        svgTextArr.append(line_)
                else:
                    svgTextArr.append(line)
            newText = ''
            for line_ in svgTextArr:
                newText += line_ + '\n'
            self.svg.getroot()[0][2][1].text = newText
            self.svg.getroot().set('xml:space','preserve')
            height = str((fontSize+2.3)*len(svgTextArr)+5)
            if float(height) < float(self.svg.getroot()[0][2][0].get('height')):
                height = self.textAreaHeight
            self.svg.getroot()[0][2][0].set('height',height)

            if not os.path.isdir('temp'): os.mkdir('temp')
            self.svg.write('temp/editedCheckbox.svg', 'utf-8')
            pixmap = QPixmap('temp/editedCheckbox.svg')
            self.setPixmap(pixmap)
            os.remove("temp/editedCheckbox.svg")
            self.deselect()
            
    def updateText(self, newText):
        self.svg.getroot()[0][2][1].text = newText

        if not os.path.isdir('temp'): os.mkdir('temp')
        self.svg.write('temp/editedCheckbox.svg', 'utf-8')
        pixmap = QPixmap('temp/editedCheckbox.svg')
        self.setPixmap(pixmap)
        os.remove("temp/editedCheckbox.svg")
        self.deselect()

    def textwidth(self, text, fontsize=7.8):
        surface = cairo.SVGSurface('undefined.svg', 1280, 200)
        cr = cairo.Context(surface)
        cr.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(fontsize)
        xbearing, ybearing, width, height, xadvance, yadvance = cr.text_extents(text)
        return width
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Shift and self.textEdit.hasFocus():
            self.firstrelease = True

    def keyReleaseEvent(self, event):
        if self.firstrelease == False:
            if event.key() == Qt.Key_Return and self.textEdit.hasFocus():
                self.saveText()
        self.firstrelease = False
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == 1:
            self.select()
            self.click_pos['x'] = event.localPos().x()
            self.click_pos['y'] = event.localPos().y()
            
            self.checkDoubleClick()
            self.timer.timeout.connect(self.timerStopped)
            self.timer.start(250)
        elif event.button() == 2:
            self.deselect()
            self.rcMenu = QPushButton('&Delete',self)
            self.rcMenu.move(round(event.pos().x()),round(event.pos().y()))
            self.rcMenu.resize(50,20)
            self.rcMenu.setStyleSheet('background-color: white; border: 1px solid gray;')
            self.rcMenu.clicked.connect(lambda:self.delete())
            self.rcMenu.show()
            pass

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.windowPos()
        self.move(round(pos.x()-self.parentEle.pos().x()-50-self.click_pos['x']),round(pos.y()-self.parentEle.pos().y()-self.click_pos['y']))
