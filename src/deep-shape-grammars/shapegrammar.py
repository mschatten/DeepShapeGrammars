#!/usr/bin/env python3
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
from gi.repository import Gimp
from gi.repository import GimpUi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gio
from gi.repository import GLib
import match_template as tm
import xml.etree.ElementTree as ET


def new_grammar1(imgGIMP, bboxes, layer):
    #znači radi na način da se treba dodati slika koja se zamijenjuje i onda se dohvati layer taj od slike. Nakon toga se kreiraju . 
    #trebam iz template matchinga dobitactive_image ove stvari ko što su shapovi, samo treba izračunati svaku posebnu stvar
    
    backgroundLayer=imgGIMP.get_layers()[-1]
    #shapes=[shape1, shape2, shape3, shape4]
    shapes=createShapes(bboxes)
    parseShapeGrammar(layer, None, shapes, imgGIMP, backgroundLayer)
    
def createShapes(bboxes):
    shapes=[]
    for bbox in bboxes:
        width=bbox[1][0]-bbox[0][0]
        height=bbox[1][1]-bbox[0][1]
        shape=Shape(bbox[0][0], bbox[0][1], width, height, 0)
        print(shape)
        shapes.append(shape)
    return shapes



def parseShapeGrammar(layer, rules, shapes, imgGIMP, bckg):
    layerGroup=createGroupLyr(layer, imgGIMP)
    for shape in shapes: 
        layerN=newLayerFromLayer(layer, layerGroup, imgGIMP)
        applyRules(layerN, rules, shape, imgGIMP, bckg)

def applyRules(layerN, rules, shape, imgGIMP, bckg):
    scaling(layerN, shape.width, shape.height, bckg)
    transporting(layerN, shape.x, shape.y)
    #rotating(layerN, shape.angle)

def createGroupLyr(layer, imgGIMP):
    layerGroup=layer.group_new(imgGIMP)
    imgGIMP.insert_layer(layerGroup, None, 0)
    return layerGroup

def newLayerFromLayer(layer, layerGroup, imgGIMP):
    layerN=layer.new_from_drawable(layer,imgGIMP)
    imgGIMP.insert_layer(layerN, layerGroup, 0)
    return layerN


#pravila
def scaling(layer, width, height, parentLyr): 
    print("scaling")
    layer.scale(width, height, parentLyr)
    #scale


def transporting(layer, x, y, parentLyr=None):
    #s obzirom na image origin hmmmm
    layer.set_offsets(x, y)
    if parentLyr is not None:
        calculateOffsets(layer, parentLyr)
    print("transporting")
    

def calculateOffsets(layer, parentLyr):
    print(parentLyr.get_offsets().offset_x)
    print(parentLyr.get_offsets().offset_y)
    print(layer.get_offsets().offset_x)
    print(layer.get_offsets().offset_y)
    x=layer.get_offsets().offset_x+parentLyr.get_offsets().offset_x
    y=layer.get_offsets().offset_y+parentLyr.get_offsets().offset_y
    layer.set_offsets(x, y)

def rotating(layer, angle): 
    #nema problema s rotacijom raznih oblika i odrezivanjem!
    print("rotating")
    rotation = (angle/180.0)*3.14159 
    width=layer.get_width()/2
    height=layer.get_height()/2
    layer.transform_rotate(rotation, True, width, height)
    

def apply_rule( rule, image ):
    m = tm.match( image, rule.LHS )
    
class Shape:
    def __init__(self, x, y, width, height, angle):
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.angle=angle
    
