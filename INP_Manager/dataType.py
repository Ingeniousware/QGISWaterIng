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
    def __init__(self, id = 0, elev = 0, demand = 0, pattern = ""):
        self.ID = id
        self.Elev = elev
        self.Demand = demand
        self.Pattern = pattern
    
    def __str__(self):
        return f" {self.ID: <15}\t{self.Elev: <12}\t{self.Demand: <12}\t{self.Pattern: <15};"

class Reservoir():
    #ID              	Head        	Pattern
    def __init__(self, id = 0, head = 0, pattern = ""):
        self.ID = id
        self.Head = head
        self.Pattern = pattern
    
    def __str__(self):
        return f" {self.ID: <15}\t{self.Head: <12}\t{self.Pattern: <15};"

class Tank():
    #ID              	Elevation   	InitLevel   	MinLevel    	MaxLevel    	Diameter    	MinVol      	VolCurve
    def __init__(self, id = 0, elevation = 0, initLevel = 0, minLevel = 0, maxLevel = 0, diameter = 0, minVol = 0, volCurve = 0):
        self.ID = id
        self.Elevation = elevation
        self.InitLevel = initLevel
        self.MinLevel = minLevel
        self.MaxLevel = maxLevel
        self.Diameter = diameter
        self.MinVol = minVol
        self.VolCurve = volCurve
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Elevation: <12}\t{self.InitLevel: <12}\t{self.MinLevel: <12}\t{self.MaxLevel: <12}\t{self.Diameter: <12}\t{self.MinVol: <12}\t{self.VolCurve: <15};"

class Pipe():
    #ID              	Node1           	Node2           	Length      	Diameter    	Roughness   	MinorLoss   	Status
    def __init__(self, id = 0, node1 = 0, node2 = 0, length = 0, diameter = 0, roughness = 0, minorLoss = 0, status = 0):
        self.ID = id
        self.Node1 = node1
        self.Node2 = node2
        self.Length = length
        self.Diameter = diameter
        self.Roughness = roughness
        self.MinorLoss = minorLoss
        self.Status = status
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Node1: <17}\t{self.Node2: <17}\t{self.Length: <12}\t{self.Diameter: <12}\t{self.Roughness: <12}\t{self.MinorLoss: <12}\t{self.Status: <15};"
    
class Pump():
    #ID              	Node1           	Node2           	Parameters
    def __init__(self, id = 0, node1 = 0, node2 = 0, pattern = ""):
        self.ID = id
        self.Node1 = node1
        self.Node2 = node2
        self.Pattern = pattern
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Node1: <17}\t{self.Node2: <17}\t{self.Pattern: <15};"

class Valve():
    #ID              	Node1           	Node2           	Diameter    	Type	Setting     	MinorLoss
    def __init__(self, id = 0, node1 = 0, node2 = 0, diameter = 0, type = 0, setting = 0, minorLoss = 0):
        self.ID = id
        self.Node1 = node1
        self.Node2 = node2
        self.Diameter = diameter
        self.Type = type
        self.Setting = setting
        self.MinorLoss = minorLoss
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.Node1: <17}\t{self.Node2: <17}\t{self.Diameter: <12}\t{self.Type: <4}\t{self.Setting: <12}\t{self.MinorLoss: <15};"
    
class Demand():
    #Junction        	Demand      	Pattern         	Category
    def __init__(self, junction = 0, demand = 0, pattern = "", category = ""):
        self.Junction = junction
        self.Demand = demand
        self.Pattern = pattern
        self.Category = category
    
    def __str__(self):
        return f" {self.Junction: <15}\t{self.Demand: <12}\t{self.Pattern: <17}\t{self.Category: <15};"
    
class Curve():
    #ID              	X-Value     	Y-Value
    def __init__(self, id = 0, x_value = 0, y_value = 0):
        self.ID = id
        self.X_value = x_value
        self.Y_value = y_value
        
    def __str__(self):
        return f" {self.ID: <15}\t{self.X_value: <12}\t{self.Y_value: <15};"
    
########################################################################Proximas clas #########################################################################
    
class Coordinate():
    #Node            	X-Coord         	Y-Coord
    def __init__(self, node = 0, x_coord = 0, y_coord = 0):
        self.Node = node
        self.X_Coord = x_coord
        self.Y_Coord = y_coord
    
    def __str__(self):
        return f" {self.Node: <15}\t{self.X_Coord: <16}\t{self.Y_Coord: <15};"
    
class Vertice():
    #Link            	X-Coord         	Y-Coord
    def __init__(self, link = 0, x_coord = 0, y_coord = 0):
        self.Link = link
        self.X_Coord = x_coord
        self.Y_Coord = y_coord
        
    def __str__(self):
        return f" {self.Link: <15}\t{self.X_Coord: <16}\t{self.Y_Coord: <15};"
    
class Label():
    #X-Coord           Y-Coord          Label & Anchor Node
    def __init__(self, x_coord = 0, y_coord = 0, anchor_node = ""):
        self.X_Coord = x_coord
        self.Y_Coord = y_coord
        self.Anchor_node = anchor_node
        
    def __str__(self):
        return f" {self.X_Coord: <15}\t{self.Y_Coord: <12}\t{self.Anchor_node: <15};"
    
################################################################ Proximas class