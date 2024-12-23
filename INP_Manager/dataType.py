# -*- coding: utf-8 -*-

"""
***************************************************************************
    sections.py
    ---------------------
    Date                 : Nomviembre 2024
    Copyright            : (C) 2024 by Ingeniowarest
    Email                : 
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Ingenioware                                                       *
*                                                                         *
***************************************************************************
"""

class Junction():
    #ID              	Elev        	Demand      	Pattern
    def __init__(self, id = "", elev = 0.0, demand = 0.0, pattern = "", description = ""):
        self.ID = id if id  else ""
        self.Elev = elev if elev else 0.0
        self.Demand = demand if demand else 0.0
        self.Pattern = pattern if pattern else ""
        self.Description = description if description else ""
    
    def __str__(self):
        return f" {self.ID: <15}\t{self.Elev: <12}\t{self.Demand: <12}\t{self.Pattern: <15};{self.Description}"

class Reservoir():
    #ID              	Head        	Pattern
    def __init__(self, id = "", head = 0.0, pattern = "", description = ""):
        self.ID = id if id  else ""
        self.Head = head if head else 0.0
        self.Pattern = pattern if pattern else ""
        self.Description = description if description else ""
    
    def __str__(self):
        return f" {self.ID: <15}\t{self.Head: <12}\t{self.Pattern: <15};{self.Description}"

class Tank():
    #ID              	Elevation   	InitLevel   	MinLevel    	MaxLevel    	Diameter    	MinVol      	VolCurve
    def __init__(self, id = "", elevation = 0.0, initLevel = 0.0, minLevel = 0.0, maxLevel = 0.0, diameter = 0.0, minVol = 0.0, volCurve = 0.0, description = ""):
        self.ID = id if id else ""
        self.Elevation = elevation if elevation else 0.0
        self.InitLevel = initLevel if initLevel else 0.0
        self.MinLevel = minLevel if minLevel else 0.0
        self.MaxLevel = maxLevel if maxLevel else 0.0
        self.Diameter = diameter if diameter else 0.0
        self.MinVol = minVol if minVol else 0.0
        self.VolCurve = volCurve if volCurve else 0.0
        self.Description = description if description else ""
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Elevation: <12}\t{self.InitLevel: <12}\t{self.MinLevel: <12}\t{self.MaxLevel: <12}\t{self.Diameter: <12}\t{self.MinVol: <12}\t{self.VolCurve: <15};{self.Description}"

class Pipe():
    #ID              	Node1           	Node2           	Length      	Diameter    	Roughness   	MinorLoss   	Status
    def __init__(self, id = "", node1 = "", node2 = "", length = 0.0, diameter = 0.0, roughness = 0.0, minorLoss = 0.0, status = "", description = ""):
        self.ID = id if id else ""
        self.Node1 = node1 if node1 else ""
        self.Node2 = node2 if node2 else ""
        self.Length = length if length else 0.0
        self.Diameter = diameter if diameter else 0.0
        self.Roughness = roughness if roughness else 0.0
        self.MinorLoss = minorLoss if minorLoss else 0.0
        self.Status = status if status else ""
        self.Description = description if description else ""
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Node1: <17}\t{self.Node2: <17}\t{self.Length: <12.4f}\t{self.Diameter: <12}\t{self.Roughness: <12}\t{self.MinorLoss: <12}\t{self.Status: <15};{self.Description}"
    
class Pump():
    #ID              	Node1           	Node2           	Parameters
    def __init__(self, id = "", node1 = 0, node2 = 0, pattern = "", description = ""):
        self.ID = id if id else ""
        self.Node1 = node1 if node1 else ""
        self.Node2 = node2 if node2 else ""
        self.Pattern = pattern if pattern else ""
        self.Description = description if description else ""
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Node1: <17}\t{self.Node2: <17}\t{self.Pattern: <15};{self.Description}"

class Valve():
    #ID              	Node1           	Node2           	Diameter    	Type	Setting     	MinorLoss
    def __init__(self, id = "", node1 = 0.0, node2 = 0.0, diameter = 0.0, type = "", setting = "", minorLoss = 0.0, description = ""):
        self.ID = id if id else ""
        self.Node1 = node1 if node1 else ""
        self.Node2 = node2 if node2 else ""
        self.Diameter = diameter if diameter else 0.0
        self.Type = type if type else ""
        self.Setting = setting if setting else ""
        self.MinorLoss = minorLoss if minorLoss else 0.0
        self.Description = description if description else ""
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Node1: <17}\t{self.Node2: <17}\t{self.Diameter: <12}\t{self.Type: <4}\t{self.Setting: <12}\t{self.MinorLoss: <15};{self.Description}"
    
class Tag():
    #Ejemplo de Tag NODE 	4               	Nodo_Terminal
    #Para nodo, tanques embales el type es NODE y para tuberias, bombas y valvulas el type es LINK
    def __init__(self, typeNode = "NODE", id = "", label = ""):
        self.Type = typeNode if typeNode else "NODE"
        self.ID = id if id else ""
        self.Label = label if label else ""
    
    def __str__(self):
        return f" {self.Type: <6}\t{self.ID: <16}\t{self.Label}"
    
class Demand():
    #Junction        	Demand      	Pattern         	Category
    def __init__(self, junction = "", demand = 0.0, pattern = "", category = ""):
        self.Junction = junction if junction else ""
        self.Demand = demand if demand else 0.0
        self.Pattern = pattern if pattern else ""
        self.Category = category if category else ""
    
    def __str__(self):
        return f" {self.Junction: <15}\t{self.Demand: <12}\t{self.Pattern: <17}\t{self.Category: <15};"
    
class Pattern():
    #ID              	Multipliers
    def __init__(self, description = "", id = "", multiplers = []):
        self.Description = description if description else ""
        self.ID = id if id else ""
        self.Multipliers = multiplers
    def __str__(self):
        text = f";{self.Description}\n {self.ID: <16}\t"
        i = 0
        for item in self.Multipliers:
            if (i < 5):
                text += f"{item: <12}\t"
            elif (i == 5):
                text += f"{item: <12}\n"
            else:
                i = -1
                text += f" {self.ID: <16}\t"
            i += 1
        return text
    
class Curve():
    #ID              	X-Value     	Y-Value
    def __init__(self, id = "", x_value = 0.0, y_value = 0.0):
        self.ID = id if id else ""
        self.X_value = x_value if x_value else 0.0
        self.Y_value = y_value if y_value else 0.0
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.X_value: <12}\t{self.Y_value: <15};"
    
######################### Proximas clas #####################################################
    
class Coordinate():
    #Node            	X-Coord         	Y-Coord
    def __init__(self, node = "", x_coord = 0.0, y_coord = 0.0):
        self.Node = node if node else ""
        self.X_Coord = x_coord if x_coord else 0.0
        self.Y_Coord = y_coord if y_coord else 0.0
    
    def __str__(self):
        return f" {self.Node: <15}\t{self.X_Coord: <16}\t{self.Y_Coord: <15};"
    
class Vertice():
    #Link            	X-Coord         	Y-Coord
    def __init__(self, link = "", x_coord = 0.0, y_coord = 0.0):
        self.Link = link if link else ""
        self.X_Coord = x_coord if x_coord else 0.0
        self.Y_Coord = y_coord if y_coord else 0.0
        
    def __str__(self):
        return f" {self.Link: <15}\t{self.X_Coord: <16}\t{self.Y_Coord: <15};"
    
class Label():
    #X-Coord           Y-Coord          Label & Anchor Node
    def __init__(self, x_coord = 0.0, y_coord = 0.0, anchor_node = ""):
        self.X_Coord = x_coord if x_coord else 0.0
        self.Y_Coord = y_coord if y_coord else 0.0
        self.Anchor_node = anchor_node if anchor_node else ""
        
    def __str__(self):
        return f" {self.X_Coord: <15}\t{self.Y_Coord: <12}\t{self.Anchor_node: <15};"
    
class Backdrop():
    def __init__(self, xmin = 0.0, ymin = 0.0, xmax = 10000.0, ymax = 10000.0, units = "Ninguno", file = "", offsetx = 0.0, offsety = 0.0):
        self.x_min = xmin if xmin else 0.0
        self.y_min = ymin if ymin else 0
        self.x_max = xmax if xmax else 0.0
        self.y_max = ymax if ymax else 0.0
        self.Units = units if units else "Ninguno"
        self.File = file if file else ""
        self.offset_x = offsetx if offsetx else 0.0
        self.offset_y = offsety if offsety else 0.0
        
    def __str__(self):
        return f" DIMENSIONS     	{self.x_min: <17}\t{self.y_min: <17}\t{self.x_max: <17}\t{self.y_max: <17}\n UNITS          	{self.Units}\n FILE           	{self.File}\n OFFSET         	{self.offset_x: <17}\t{self.offset_y: <17}"
################################################################ Proximas class