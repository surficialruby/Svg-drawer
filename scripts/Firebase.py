import json
import configparser
from firebase_admin import db
from . import objectController as oc

def fbGetMaps():
    ref = db.reference('maps/')
    maps = ref.get()
    return maps

def fbSave():
    config = configparser.ConfigParser()
    config.read('config\settings.ini')
    ref = db.reference('maps/')
    if oc.savedID:
        fbUpdate(ref,config)
    else:
        fbPush(ref, config)

def fbPush(ref, config):
    with open('out/'+ config['save']['name'] +'.json', 'r') as f:
        file_contents = json.load(f)
    key = ref.push(file_contents).key
    oc.updateID(key)

def fbUpdate(ref, config):
    with open('out/'+ config['save']['name'] +'.json', 'r') as f:
        file_contents = json.load(f)
    ref.child(oc.savedID).set(file_contents)

def fbLoad():
    pass