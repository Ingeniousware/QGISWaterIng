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

"""
Ejemplo de como crear un grupo en QGIS.

    from qgis.core import QgsProject, QgsLayerTreeGroup

    # Obtener el proyecto actual
    project = QgsProject.instance()

    # Crear un nuevo grupo
    nuevo_grupo = QgsLayerTreeGroup("Nombre del Grupo")

    # Añadir el grupo al árbol de capas del proyecto
    project.layerTreeRoot().addChildNode(nuevo_grupo)

    print("Grupo añadido exitosamente.")
    
    Este script realiza las siguientes acciones:

        1-Crea una nueva capa vectorial a partir de un archivo shapefile.
        2-Verifica si la capa se ha cargado correctamente.
        3-Obtiene el proyecto actual de QGIS.
        4-Crea un nuevo grupo en el árbol de capas.
        5-Añade la capa al grupo recién creado.
        
    from qgis.core import QgsProject, QgsVectorLayer

    # Crear una nueva capa vectorial
    capa = QgsVectorLayer("path/to/your/shapefile.shp", "Nombre de la Capa", "ogr")

    # Verificar si la capa se ha cargado correctamente
    if not capa.isValid():
        print("La capa no se pudo cargar.")
    else:
        # Obtener el proyecto actual
        proyecto = QgsProject.instance()

        # Crear un nuevo grupo
        grupo = proyecto.layerTreeRoot().addGroup("Nombre del Grupo")

        # Añadir la capa al grupo
        grupo.addLayer(capa)

        print("Capa añadida al grupo exitosamente.")
    
    Este script hace lo siguiente:

        1-Crea una nueva capa vectorial en memoria con un sistema de referencia EPSG:4326 y dos campos: id (entero) y name (cadena de 20 caracteres).
        2-Verifica si la capa se ha creado correctamente.
        3-Añade la capa al proyecto QGIS sin mostrarla inmediatamente en el panel de capas.
        4-Busca un grupo llamado "Mi Grupo" en el árbol de capas. Si no existe, lo crea.
        5-Añade la nueva capa al grupo especificado.
    
    from qgis.core import QgsProject, QgsVectorLayer, QgsLayerTreeGroup

    # Crear una nueva capa vectorial (por ejemplo, una capa de puntos)
    uri = "Point?crs=EPSG:4326&field=id:integer&field=name:string(20)&index=yes"
    new_layer = QgsVectorLayer(uri, "Nueva Capa de Puntos", "memory")

    # Verificar si la capa se ha creado correctamente
    if not new_layer.isValid():
        print("La capa no se ha creado correctamente")
    else:
        # Añadir la capa al proyecto
        QgsProject.instance().addMapLayer(new_layer, False)

        # Obtener el grupo al que queremos añadir la capa
        root = QgsProject.instance().layerTreeRoot()
        group_name = "Mi Grupo"
        group = root.findGroup(group_name)

        # Si el grupo no existe, crearlo
        if group is None:
            group = root.addGroup(group_name)

        # Añadir la capa al grupo
        group.addLayer(new_layer)

        print(f"La capa '{new_layer.name()}' se ha añadido al grupo '{group_name}' correctamente.")
"""

import os
import stat

from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsFields, QgsRenderContext, QgsVectorLayer, QgsProject
from qgis.core import QgsProject, QgsField
from PyQt5.QtCore import QVariant


from .sections import (sectionTitle, sectionJunctions, sectionReservoirs, sectionTanks, sectionPipes, sectionPumps,
                       sectionValves, sectionTags, sectionDemands, sectionStatus, sectionPatterns, sectionCurves,
                       sectionControls, sectionRules, sectionEnergy, sectionEmitters, sectionQuality, sectionSources,
                       sectionReactions, sectionReactions20, sectionMixing, sectionTimes, sectionReport, sectionOptions,
                       sectionCoordinates, sectionVertices, sectionLabels, sectionBackdrop, sectionEnd)
from .dataType import (Junction, Reservoir, Tank, Pipe, Pump, Valve, Tag, Demand, Curve, Coordinate, Vertice, Label,
                       Backdrop)

import json
import os
#import wntr.resultTypes as rt
#from ..wntr.resultTypes import
from ..watering_utils import WateringUtils
from ..wntr.epanet.toolkit import ENepanet
from ..wntr.epanet.util import EN
from ..wntr.resultTypes import ResultNode, ResultLink
from .inp_utils import INP_Utils
from ..NetworkAnalysis.nodeNetworkAnalysisLocal import NodeNetworkAnalysisLocal


class INPManager():
    def __init__(self):
        self._outfile: str = ""
        self._nodes = {}
        # self._outfile = self.__getScenarioFolderPath()
        
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


    @property
    def OutFile(self):
        if self._outfile == "":
            self._outfile = self.__getWorkingDirectory()
        return self._outfile
    @OutFile.setter
    def OutFile(self, value: str):
        self._outfile = value

    @property
    def Out_Folder_Path_INP(self):
        return os.path.splitext(self.OutFile)


    def __getWorkingDirectory(self):
        workingDirectory = INP_Utils.default_working_directory()
        
        workingDirectory = workingDirectory + "\\localScenario.inp"
        
        return workingDirectory


    def __updateDictionaryNode(self, id, name):
        self._nodes[id] = name


    def __getValueNodes(self, key):
        for itemKey in self._nodes.keys():
            if itemKey == key:
                return self._nodes[itemKey]
        return None


    def __readFeatures(self, layerName):
        source_layer = QgsProject.instance().mapLayersByName(layerName)[0]
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
        
            name = feature.attribute("Name") #if feature.attribute("Name") is not None else ""
            elev = feature.attribute("Z[m]") #if feature.attribute("Z[m]") is not None else 0.0
            demand = feature.attribute("B. Demand") #if feature.attribute("B. Demand") is not None else ""
            pattern = feature.attribute("EmitterCoe") #if feature.attribute("EmitterCoe") is not None else ""
            description = feature.attribute("Descript") #if feature.attribute("Descript") is not None else ""
            label = "" #Esto es para escribir las etiquetas de epanet.
            
            coordinate.values.append(Coordinate(name, pointXY.x(), pointXY.y()))
            
            junctions.values.append(Junction(name, elev, demand, pattern, description))
            
            if label != "":
                tag.values.append(Tag("NODE", name, label))
            
            self.__updateDictionaryNode(feature.attribute("ID"), name)


    def __readReservoirs(self, layerName = "watering_reservoirs"):
        
        source_layer = QgsProject.instance().mapLayersByName(layerName)[0]
        features = source_layer.getFeatures() #self.__readFeatures(layerName)
        
        coordinate = self.sections['COORDINATES']
        reservoirs = self.sections['RESERVOIRS']
        tag = self.sections['TAGS']
        
        for feature in features:
            pointXY = feature.geometry().asPoint()
            name = feature.attribute("Name") #if feature.attribute("Name") is not None else ""
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
            
            coordinate.values.append(Coordinate(name, pointXY.x(), pointXY.y()))
            
            reservoirs.values.append(Reservoir(name, head, pattern, description))
            
            if label != "":
                tag.values.append(Tag("NODE", name, label))
            
            self.__updateDictionaryNode(feature.attribute("ID"), name)


    def __readTanks(self, layerName = "watering_tanks"):
        
        source_layer = QgsProject.instance().mapLayersByName(layerName)[0]
        features = source_layer.getFeatures() #self.__readFeatures(layerName)
        
        coordinate = self.sections['COORDINATES']
        tank = self.sections['TANKS']
        tag = self.sections['TAGS']
        
        for feature in features:
            pointXY = feature.geometry().asPoint()
            name = feature.attribute("Name") #if feature.attribute("Name") is not None else ""
            elevation = feature.attribute("Z[m]") #if feature.attribute("Z[m]") is not None else 0.0
            initLevel = feature.attribute("Init. Lvl") #if feature.attribute("Init. Lvl") is not None else 0.0
            minLevel = feature.attribute("Min. Lvl") #if feature.attribute("Min. Lvl") is not None else 0.0
            maxLevel = feature.attribute("Max. Lvl") #if feature.attribute("Max. Lvl") is not None else 0.0
            diameter = feature.attribute("Diameter") #if feature.attribute("Diameter") is not None else 0.0
            minVol = feature.attribute("Min. Vol.") #if feature.attribute("Min. Vol.") is not None else 0.0
            volCurve = ""
            description = feature.attribute("Descript") #if feature.attribute("Descript") is not None else ""
            label = "" #Esto es para escribir las etiquetas de epanet.
            
            coordinate.values.append(Coordinate(name, pointXY.x(), pointXY.y()))
            
            tank.values.append(Tank(name, elevation, initLevel, minLevel, maxLevel, diameter, minVol, volCurve, description))
            
            if label != "":
                tag.values.append(Tag("NODE", name, label))
                
            self.__updateDictionaryNode(feature.attribute("ID"), name)


    def __readPipes(self, layerName = "watering_pipes"):
        
        source_layer = QgsProject.instance().mapLayersByName(layerName)[0]
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
            node1Name = self.__getValueNodes(node1)
            node2Name = self.__getValueNodes(node2)
            
            # geom = feature.geometry()
            # vert = 0
            # for part in geom.parts():
            #     for vertex in part.vertices():
            #         if part.startPoint() == geom.vertexAt(vert):
            #             coordinate.values.append(Coordinate(node1, part.startPoint().x(), part.startPoint().y()))
            #         elif part.endPoint() == geom.vertexAt(vert):
            #             coordinate.values.append(Coordinate(node2, part.endPoint().x(), part.endPoint().y()))
            #         else:
            #             vertice.values.append(Vertice(id, vertex.x(), vertex.y()))
            #         vert += 1
            
            pipe.values.append(Pipe(id, node1Name, node2Name, length, diameter, roughness, minorLoss, status, description))
            
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


    def writeSections(self):
        self.__readLayers()
        
        with open(os.path.join(self.OutFile), "w") as inpfile:
            for t, s in self.sections.items():
                print(t, s.name)
                s.writeSection(inpfile)

        # Cierra el fichero manualmente
        # self.outfile.close()


    # def updateLayer(self):
    #     layer_1 = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]

    #     # Verificar si la capa es válida
    #     if not layer_1:
    #         print("No hay una capa activa.")
    #     else:
    #         # Definir el nombre de la nueva propiedad (campo)
    #         new_field_name = "Pressure"

    #         # Verificar si la propiedad ya existe
    #         existing_fields = [field.name() for field in layer_1.fields()]
    #         if new_field_name in existing_fields:
    #             print(f"La propiedad '{new_field_name}' ya existe en la capa.")
    #         else:
    #             # Añadir la nueva propiedad
    #             # Iniciar edición
    #             print("actulaizando el layer")
    #             layer_1.startEditing()
    #             new_field = QgsField(new_field_name, QVariant.String)
    #             layer_1.dataProvider().addAttributes([new_field])
    #             layer_1.updateFields()
    #             print(f"La propiedad '{new_field_name}' ha sido añadida a la capa.")


    def __getidNode(self, espanet: ENepanet, nodeName: str, count: int):
        result = 0
        
        for i in range(1, count + 1):
            a = espanet.ENgetnodeid(i)
            if a == nodeName:
                result = i
                break
        return result


    def getAnalysisResults(self):
        """Se obtienen los resultados de la simulación local"""
        # Seeliminan los layes que se crearon para motrar los resultados
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if shapeGroup:
            layer_ids = [layer.layerId() for layer in shapeGroup.findLayers()]
            root.removeChildNode(shapeGroup)
            for layer_id in layer_ids:
                QgsProject.instance().removeMapLayer(layer_id)
        
        rptfile=None
        binfile=None
        inpfile = self.OutFile
        file_prefix, file_ext = os.path.splitext(inpfile)
        if rptfile is None:
            rptfile = file_prefix + ".rpt"
        if binfile is None:
            binfile = file_prefix + ".bin"
        
        try:
            enData = ENepanet()
            enData.ENopen(inpfile, rptfile, binfile)
            #enData.ENsolveH()
           
            analysis = NodeNetworkAnalysisLocal(enData, "1000-2221-45", "23:12")
            #analysis.runAnalysis()
            
            enData.ENclose()
            
        except Exception as e:
            raise e


    def testEpanet(self, inpfile = "C:\\Temp\\Net1.inp", rptfile=None, binfile=None):
        """
        Run an EPANET command-line simulation
        
        Parameters
        ----------
        inpfile : str
            The input file name
        """
        file_prefix, file_ext = os.path.splitext(inpfile)
        if rptfile is None:
            rptfile = file_prefix + ".rpt"
        if binfile is None:
            binfile = file_prefix + ".bin"
        
        try:
            enData = ENepanet()
            enData.ENopen(inpfile, rptfile, binfile)
            enData.ENsolveH()
            #enData.ENsolveQ() #Para el caso del análisis de la calidad del agua.
            # try:
            #     enData.ENreport()
            # except:
            #     pass
            
            nNodes = enData.ENgetcount(EN.NODECOUNT)
            print("Cantidad de nodos: ", nNodes)
            
            # layer_1 = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
            # # Iniciar edición de la capa
            # layer_1.startEditing()
            
            valoresNodes = []
            for i in range(1, nNodes + 1):
                a = enData.ENgetnodeid(i)#.ENgetnodevalue(i, EN.BASEDEMAND)
                b = enData.ENgetnodevalue(i, EN.DEMAND)
                c = enData.ENgetnodevalue(i, EN.PRESSURE)
                d = enData.ENgetnodevalue(i, EN.HEAD)
                valoresNodes.append(ResultNode(a, b, c, d))
            
            # features = layer_1.getFeatures()
            # for feature in features:
            #     nodeName = feature.attribute("Name")
            #     item = self.__getidNode(enData, nodeName, nNodes)
            #     pressure = enData.ENgetnodevalue(item, EN.PRESSURE)
            #     feature.setAttribute("Pressure", pressure)
            #     # Actualizar la característica en la capa
            #     layer_1.updateFeature(feature)
            # # Guardar cambios
            # layer_1.commitChanges()
                
            
            # Paso 3: Escribe la lista en un archivo JSON
            jsonFile = file_prefix + "Node" + ".json"
            with open(jsonFile, 'w') as archivo_json:
                json.dump([item.to_dict() for item in valoresNodes], archivo_json, ensure_ascii = False, indent = 4)
            
            nLinks = enData.ENgetcount(EN.LINKCOUNT)
            print("Cantidad de tuberias: ", nLinks)
            
            linkResult = []
            
            for i in range(1, nLinks + 1):
                a = enData.ENgetlinkvalue(i, EN.LPS)
                b = enData.ENgetlinkvalue(i, EN.HEADLOSS)
                c = enData.ENgetlinkvalue(i, EN.STATUS)
                d = enData.ENgetlinkvalue(i, EN.DIAMETER)
                g = enData.ENgetlinkvalue(i, EN.MINORLOSS)
                linkResult.append(ResultLink(a, b, c, d, g))
                
            # Paso 3: Escribe la lista en un archivo JSON
            jsonFile = file_prefix + "Link" + ".json"
            with open(jsonFile, 'w') as archivo_json:
                json.dump([item.to_json() for item in linkResult], archivo_json, ensure_ascii=False, indent=4)
            
            flows = enData.ENgetflowunits()
            if flows == 0: UndCaudal = "CFS"
            if flows == 1: UndCaudal = "GPM"
            if flows == 2: UndCaudal = "MGD"
            if flows == 3: UndCaudal = "IMGD"
            if flows == 4: UndCaudal = "AFD"
            if flows == 5: UndCaudal = "LPS"
            if flows == 6: UndCaudal = "LPM"
            if flows == 7: UndCaudal = "MLD"
            if flows == 8: UndCaudal = "CMH"
            if flows == 9: UndCaudal = "CMD"
            print("Unidad de caudal: ", UndCaudal)
           
            print("Termine el análisis...")
            enData.ENclose()
        
        except Exception as e:
            raise e