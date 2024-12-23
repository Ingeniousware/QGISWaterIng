# -*- coding: utf-8 -*-

"""
***************************************************************************
    INPManager.py
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

from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsFields, QgsRenderContext, QgsVectorLayer, QgsProject

from .sections import sectionTitle, sectionJunctions, sectionReservoirs, sectionTanks, sectionPipes, sectionPumps, sectionValves, sectionTags, sectionDemands, sectionStatus, sectionPatterns, sectionCurves, sectionControls, sectionRules, sectionEnergy, sectionEmitters, sectionQuality, sectionSources, sectionReactions, sectionReactions20, sectionMixing, sectionTimes, sectionReport, sectionOptions, sectionCoordinates, sectionVertices, sectionLabels, sectionBackdrop, sectionEnd
from .dataType import Junction, Reservoir, Tank, Pipe, Pump, Valve, Tag, Demand, Curve, Coordinate, Vertice, Label, Backdrop

class INPManager():
    def __init__(self, outfile=None):
        self.outfile = outfile
        
        #list1.First(ii => ii.id == "")
        #next((item for item in list1 if item.id == ""), None)
        
        self.xmin = 0.0
        self.ymin = 0.0
        self.xmax = 10000.0
        self.ymax = 10000.0

        self.sections = {'TITLE': sectionTitle('PRUEBA DE INP'),
                         'JUNCTIONS': sectionJunctions(),
                         'RESERVOIRS': sectionReservoirs(),
                         'TANKS': sectionTanks(),
                         'PIPES': sectionPipes(),
                         'PUMPS': sectionPumps(),
                         'VALVES': sectionValves(),
                         'TAGS': sectionTags(),
                         'DEMANDS': sectionDemands(),
                         'STATUS': sectionStatus(),
                         'PATTERNS': sectionPatterns(),
                         'CURVES': sectionCurves(),
                         'CONTROLS': sectionControls(),
                         'RULES': sectionRules(),
                         'ENERGY': sectionEnergy(),
                         'EMITTERS': sectionEmitters(),
                         'QUALITY': sectionQuality(),
                         'SOURCES': sectionSources(),
                         'REACTIONS': sectionReactions(),
                         'REACTIONS20': sectionReactions20(),
                         'MIXING': sectionMixing(),
                         'TIMES': sectionTimes(),
                         'REPORT': sectionReport(),
                         'OPTIONS': sectionOptions(),
                         'COORDINATES': sectionCoordinates(),
                         'VERTICES': sectionVertices(),
                         'LABELS': sectionLabels(),
                         'BACKDROP': sectionBackdrop(),
                         'END': sectionEnd()}
        
    def __readFeatures(self, layerName):
        source_layer = QgsProject.instance().mapLayersByName(layerName)[1]
        print(source_layer)
        return source_layer.getFeatures()
    
    def __readDemandNode(self, layerName = "watering_demand_nodes"):
        source_layer = QgsProject.instance().mapLayersByName(layerName)[0]
        features = source_layer.getFeatures() #self.__readFeatures(layerName)
        # Define the source and destination coordinate reference systems
        crs_source = source_layer.crs()
        crs_destination = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS84
        transform = QgsCoordinateTransform(crs_source, crs_destination, QgsProject.instance())
            
        coordinate = self.sections['COORDINATES']
        junctions = self.sections['JUNCTIONS']
        tag = self.sections['TAGS']
        
        for feature in features:
            pointXY = feature.geometry().asPoint()
            #transformed_point = transform.transform(pointXY)
            #print(f"Imprimiento puntos {transformed_point}")
        
            id = feature.attribute("Name") #if feature.attribute("Name") is not None else ""
            elev = feature.attribute("Z[m]") #if feature.attribute("Z[m]") is not None else 0.0
            demand = feature.attribute("B. Demand") #if feature.attribute("B. Demand") is not None else ""
            pattern = feature.attribute("EmitterCoe") #if feature.attribute("EmitterCoe") is not None else ""
            description = feature.attribute("Descript") #if feature.attribute("Descript") is not None else ""
            label = "" #Esto es para escribir las etiquetas de epanet.
            
            coordinate.values.append(Coordinate(id, pointXY.x(), pointXY.y()))
            
            junctions.values.append(Junction(id, elev, demand, pattern, description))
            
            if label != "":
                tag.values.append(Tag("NODE", id, label))
    
    def __readReservoirs(self, layerName = "watering_reservoirs"):
        
        source_layer = QgsProject.instance().mapLayersByName(layerName)[1]
        features = source_layer.getFeatures() #self.__readFeatures(layerName)
        
        coordinate = self.sections['COORDINATES']
        reservoirs = self.sections['RESERVOIRS']
        tag = self.sections['TAGS']
        
        for feature in features:
            pointXY = feature.geometry().asPoint()
            id = feature.attribute("Name") #if feature.attribute("Name") is not None else ""
            #elev = feature.attribute("Z[m]") if feature.attribute("Z[m]") is not None else ""
            head = feature.attribute("Head[m]") #if feature.attribute("Head[m]") is not None else 0.0
            pattern = ""
            description = feature.attribute("Descript") #if feature.attribute("Descript") is not None else ""
            label = "" #Esto es para escribir las etiquetas de epanet.
            
            # layer = QgsProject.instance().mapLayersByName("watering_reservoirs")[1]
            # layer_tree_root = QgsProject.instance().layerTreeRoot()
            # layer_tree_layer = layer_tree_root.findLayer(layer)
            # #layer_is_visible = layer_tree_layer.isVisible()
            # #print(layer_is_visible)
            # visibleFeatures = []
            # renderer = layer.renderer().clone()
            # ctx = QgsRenderContext()
            # renderer.startRender(ctx, QgsFields())
            # for feature in layer.selectedFeatures():
            #     ctx.expressionContext().setFeature(feature)
            #     if renderer.willRenderFeature(feature, ctx):
            #         visibleFeatures.append(feature)
            # renderer.stopRender(ctx)
            # print(visibleFeatures)
            # visibleFeatures.append("Carlos")
            # print(visibleFeatures)
            
            coordinate.values.append(Coordinate(id, pointXY.x(), pointXY.y()))
            
            reservoirs.values.append(Reservoir(id, head, pattern, description))
            
            if label != "":
                tag.values.append(Tag("NODE", id, label))

    def __readTanks(self, layerName = "watering_tanks"):
        
        source_layer = QgsProject.instance().mapLayersByName(layerName)[0]
        features = source_layer.getFeatures() #self.__readFeatures(layerName)
        
        coordinate = self.sections['COORDINATES']
        tank = self.sections['TANKS']
        tag = self.sections['TAGS']
        
        for feature in features:
            pointXY = feature.geometry().asPoint()
            id = feature.attribute("Name") #if feature.attribute("Name") is not None else ""
            elevation = feature.attribute("Z[m]") #if feature.attribute("Z[m]") is not None else 0.0
            initLevel = feature.attribute("Init. Lvl") #if feature.attribute("Init. Lvl") is not None else 0.0
            minLevel = feature.attribute("Min. Lvl") #if feature.attribute("Min. Lvl") is not None else 0.0
            maxLevel = feature.attribute("Max. Lvl") #if feature.attribute("Max. Lvl") is not None else 0.0
            diameter = feature.attribute("Diameter") #if feature.attribute("Diameter") is not None else 0.0
            minVol = feature.attribute("Min. Vol.") #if feature.attribute("Min. Vol.") is not None else 0.0
            volCurve = ""
            description = feature.attribute("Descript") #if feature.attribute("Descript") is not None else ""
            label = "" #Esto es para escribir las etiquetas de epanet.
            
            coordinate.values.append(Coordinate(id, pointXY.x(), pointXY.y()))
            
            tank.values.append(Tank(id, elevation, initLevel, minLevel, maxLevel, diameter, minVol, volCurve, description))
            
            if label != "":
                tag.values.append(Tag("NODE", id, label))
    
    def __readPipes(self, layerName = "watering_pipes"):
        
        source_layer = QgsProject.instance().mapLayersByName(layerName)[1]
        features = source_layer.getFeatures() #self.__readFeatures(layerName)
        
        coordinate = self.sections['COORDINATES']
        vertice = self.sections['VERTICES']
        pipe = self.sections['PIPES']
        tag = self.sections['TAGS']
        
        for feature in features:
            id = feature.attribute("Name") #if feature.attribute("Name") is not None else 0.0
            node1 = feature.attribute("Up-Node") #if feature.attribute("Up-Node") is not None else 0.0
            node2 = feature.attribute("Down-Node") #if feature.attribute("Down-Node") is not None else 0.0
            length = feature.attribute("Length") #if feature.attribute("Length") is not None else 0.0
            diameter = feature.attribute("Diameter") #if feature.attribute("Diameter") is not None else 0.0
            roughness = feature.attribute("Rough.A") #if feature.attribute("Rough.A") is not None else 0.0
            minorLoss = 0
            status = "Open"
            description = feature.attribute("Descript") #if feature.attribute("Descript") is not None else ""
            label = "" #Esto es para escribir las etiquetas de epanet.
            
            geom = feature.geometry()
            vert = 0
            for part in geom.parts():
                for vertex in part.vertices():
                    if part.startPoint() == geom.vertexAt(vert):
                        coordinate.values.append(Coordinate(node1, part.startPoint().x(), part.startPoint().y()))
                    elif part.endPoint() == geom.vertexAt(vert):
                        coordinate.values.append(Coordinate(node2, part.endPoint().x(), part.endPoint().y()))
                    else:
                        vertice.values.append(Vertice(id, vertex.x(), vertex.y()))
                    vert += 1
            
            pipe.values.append(Pipe(id, node1, node2, length, diameter, roughness, minorLoss, status, description))
            
            """
            pipe_feature.setAttribute("C(H.W.)", 0)
            """
            
            if label != "":
                tag.values.append(Tag("LINK", id, label))
    
    def __Pumps(self, layerName = "watering_pumps"):
        features = self.__readFeatures(layerName)
        for feature in features:
            id = feature.attribute("Name") #if feature.attribute("Name") is not None else 0.0
            node1 = feature.attribute("Up-Node") #if feature.attribute("Up-Node") is not None else 0.0
            node2 = feature.attribute("Down-Node") #if feature.attribute("Down-Node") is not None else 0.0
            #parameters
        
        
        
        """
        ID              	Node1           	Node2           	Parameters
        new_feature.setAttribute("Name", name)
        new_feature.setAttribute("Descript", description)
        new_feature.setAttribute("Z[m]", z)
        new_feature.setAttribute("Model FK", modelFK)
        new_feature.setAttribute("Rel.Speed", relativeSpeed)
        """
    
    
    def __readBackdrop(self):
        coordinate = self.sections['COORDINATES']
        self.xmin = self.xmax = coordinate.values[0].X_Coord
        self.ymin = self.ymax = coordinate.values[0].Y_Coord
        
        self.xmin = min(item.X_Coord for item in coordinate.values)
        self.ymin  = min(item.Y_Coord for item in coordinate.values)
        
        self.xmax = max(item.X_Coord for item in coordinate.values)
        self.ymax = max(item.Y_Coord for item in coordinate.values)
        
        backdrop = self.sections['BACKDROP']
        backdrop.values.append(Backdrop(self.xmin, self.ymin, self.xmax, self.ymax))
    
    def __readLayers(self):
        self.__readDemandNode()
        self.__readReservoirs()
        self.__readTanks()
        self.__readPipes()
        
        self.__readBackdrop()

    def writeSections(self, outfile=None):
        if outfile is not None:
            self.outfile = outfile

        self.__readLayers()
        
        for t, s in self.sections.items():
            print(t,s.name)
            s.writeSection(self.outfile)
            