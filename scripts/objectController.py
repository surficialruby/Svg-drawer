elements = []
bg = ''
preset = ''
projectName = ''
savedID = ''

def updateID(id):
   global savedID
   savedID = id

def getSavedID():
   return savedID

def add(obj):
   elements.append(obj)
   elements[len(elements)-1].show()

def addBG(obj):
   global bg
   bg = obj
   return bg.filename

def addPreset(name):
   global preset
   preset = name
   return preset

def select():
   pass

def deselectAll():
   for ele in elements:
      ele.deselect()