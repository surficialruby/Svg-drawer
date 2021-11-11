import os
import configparser
import json
from svgutils import transform
import xml.etree.ElementTree as ET
from . import objectController as oc
from .Firebase import *

background = transform.SVGFigure
imgFilesData = {}
mapData = {}

def saveInit():
    config = configparser.ConfigParser()
    config.read('config\settings.ini')

    if not os.path.isdir('out'): os.mkdir('out')
    mapData = {}
    if oc.savedID: mapData['URL'] = config['save']['URL']
    else: mapData['URL'] = config['save']['URL'] + config['save']['name'] + '.svg'
    mapData['MAP'] = {}
    mapData['MAP']['name'] = config['save']['name']
    # Get checkboxes and add create map area
    for idx, img in enumerate(oc.elements):
        imgFilesData[idx] = {'file': img.svg}
        x = int(imgFilesData[idx]['file'].find('''.//*[@id='checkbox']''').get('x'))
        y = int(imgFilesData[idx]['file'].find('''.//*[@id='checkbox']''').get('y'))
        width= int(imgFilesData[idx]['file'].find('''.//*[@id='checkbox']''').get('width'))
        height = int(imgFilesData[idx]['file'].find('''.//*[@id='checkbox']''').get('height'))
        imgFilesData[idx]['file'].getroot()[0].set('id','checkbox_'+str(idx))
        imgFilesData[idx]['root'] = transform.fromstring(ET.tostring(imgFilesData[idx]['file'].getroot(),'unicode')).getroot()
        imgFilesData[idx]['root'].moveto(img.pos().x(), img.pos().y())
        if not 'areas' in mapData['MAP']: mapData['MAP']['areas'] = []
        mapData['MAP']['areas'].append({
            'id': config['save']['idPrefix'] + str(idx) + config['save']['idSuffix'],
            'shape': config['save']['shape'],
            'coords': [
                img.pos().x()*float(config['save']['mapScaleFix'])+x,
                img.pos().y()*float(config['save']['mapScaleFix'])+y,
                (img.pos().x()+x+width)*float(config['save']['mapScaleFix']),
                (img.pos().y()+x+height)*float(config['save']['mapScaleFix']),
            ],
            'preFillColor': config['save']['preFillColor'],
            'fillColor': config['save']['fillColor'],
            'strokeColor': config['save']['strokeColor']
        })
    # Save svg image xml:space="preserve"
    svg = oc.bg.svg.getroot()
    background = transform.fromstring(ET.tostring(svg).decode())
    background.append([s['root'] for s in imgFilesData.values()])
    background.save('out/'+ config['save']['name'] +'.svg','utf-8')

    # Save json map file
    with open('out/'+ config['save']['name'] +'.json', 'w', encoding='utf-8') as f:
        mapJsonPretty = json.loads(json.dumps(mapData))
        json.dump(mapJsonPretty, f, ensure_ascii=False, indent=4)

def save():
    # Create file & map
    saveInit()
    # Push json map to Firebase
    fbSave()

def saveAs():
    pass