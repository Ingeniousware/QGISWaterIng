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

import os
import stat
import uuid

import numpy as np
import matplotlib.pyplot as plt
from pandas import Series


from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsFields, QgsRenderContext, QgsVectorLayer, QgsProject # type: ignore
from qgis.core import QgsProject, QgsField # type: ignore
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import Qt
from qgis.utils import iface # type: ignore
from PyQt5 import QtCore, QtGui, QtWidgets

from .sections import (sectionTitle, sectionJunctions, sectionReservoirs, sectionTanks, sectionPipes, sectionPumps,
                       sectionValves, sectionTags, sectionDemands, sectionStatus, sectionPatterns, sectionCurves,
                       sectionControls, sectionRules, sectionEnergy, sectionEmitters, sectionQuality, sectionSources,
                       sectionReactions, sectionReactions20, sectionMixing, sectionTimes, sectionReport, sectionOptions,
                       sectionCoordinates, sectionVertices, sectionLabels, sectionBackdrop, sectionEnd)
from .dataType import (Junction, Reservoir, Tank, Pipe, Pump, TimeOptions, Valve, Tag, Demand, Curve, Coordinate, Vertice, Label,
                       Backdrop)

import json
import os
import wntr
#import wntr.resultTypes as rt
#from ..wntr.resultTypes import
from ..watering_utils import WateringUtils
# from ..wntr.epanet.toolkit import ENepanet
# from ..wntr.epanet.util import EN
# from ..wntr.resultTypes import ResultNode, ResultLink
from .inp_utils import INP_Utils
from ..NetworkAnalysis.nodeNetworkAnalysisLocal import NodeNetworkAnalysisLocal
from ..NetworkAnalysis.pipeNetworkAnalysisLocal import PipeNetworkAnalysisLocal
from .node_link_ResultType import NodeResultType, LinkResultType
from .inp_options_enum import INP_Options
from ..ui.watering_inp_options import WateringINPOptionsDialog
from .inp_options import INPOptions
# from __future__ import annotations

class INPManager():
    def __init__(self):
        self._outfile: str = ""
        # self._options = options
        # self._outfile = self.__getScenarioFolderPath()

        #list1.First(ii => ii.id == "")
        #next((item for item in list1 if item.id == ""), None)

        self.xmin = 0.0
        self.ymin = 0.0
        self.xmax = 10000.0
        self.ymax = 10000.0
        
        self.options: INPOptions = INPOptions(self)
        self.options.load()
        self._simulation_validity = False
        self._guid = ""

        self.sections = {'TITLE': sectionTitle(self, 'PRUEBA DE INP'),
                         'JUNCTIONS': sectionJunctions(self),
                         'RESERVOIRS': sectionReservoirs(self),
                         'TANKS': sectionTanks(self),
                         'PIPES': sectionPipes(self),
                         'PUMPS': sectionPumps(self),
                         'VALVES': sectionValves(self),
                         'TAGS': sectionTags(self),
                         'DEMANDS': sectionDemands(self),
                         'STATUS': sectionStatus(self),
                         'PATTERNS': sectionPatterns(self),
                         'CURVES': sectionCurves(self),
                         'CONTROLS': sectionControls(self),
                         'RULES': sectionRules(self),
                         'ENERGY': sectionEnergy(self),
                         'EMITTERS': sectionEmitters(self),
                         'QUALITY': sectionQuality(self),
                         'SOURCES': sectionSources(self),
                         'REACTIONS': sectionReactions(self),
                         'REACTIONS20': sectionReactions20(self),
                         'MIXING': sectionMixing(self),
                         'TIMES': sectionTimes(self),
                         'REPORT': sectionReport(self),
                         'OPTIONS': sectionOptions(self),
                         'COORDINATES': sectionCoordinates(self),
                         'VERTICES': sectionVertices(self),
                         'LABELS': sectionLabels(self),
                         'BACKDROP': sectionBackdrop(self),
                         'END': sectionEnd(self)}


    @property
    def OutFile(self):
        if self._outfile == "":
            self._outfile = self.__getWorkingDirectory()
        return self._outfile
    # @OutFile.setter
    # def OutFile(self, value: str):
    #     self._outfile = value

    @property
    def Out_Folder_Path_INP(self):
        return os.path.splitext(self.OutFile)


    def __getWorkingDirectory(self):
        workingDirectory = INP_Utils.default_working_directory()

        workingDirectory = workingDirectory + "\\localScenario.inp"

        return workingDirectory


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

            my_id = str(feature.attribute("ID"))
            INP_Utils.add_element(my_id, [name, 'node'])


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

            my_id = str(feature.attribute("ID"))
            INP_Utils.add_element(my_id, [name, 'node'])


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

            my_id = str(feature.attribute("ID"))
            INP_Utils.add_element(my_id, [name, 'node'])


    def __readPipes(self, layerName = "watering_pipes"):

        source_layer = QgsProject.instance().mapLayersByName(layerName)[0]
        features = source_layer.getFeatures() #self.__readFeatures(layerName)

        coordinate = self.sections['COORDINATES']
        vertice = self.sections['VERTICES']
        pipe = self.sections['PIPES']
        tag = self.sections['TAGS']

        for feature in features:
            name = feature.attribute("Name") #if feature.attribute("Name") is not None else 0.0
            node1 = feature.attribute("Up-Node") #if feature.attribute("Up-Node") is not None else 0.0
            node2 = feature.attribute("Down-Node") #if feature.attribute("Down-Node") is not None else 0.0
            length = feature.attribute("Length") #if feature.attribute("Length") is not None else 0.0
            diameter = feature.attribute("Diameter") * 1000 #if feature.attribute("Diameter") is not None else 0.0
            roughness = feature.attribute("Rough.A") #if feature.attribute("Rough.A") is not None else 0.0
            c_H_W = feature.attribute("C(H.W.)")
            minorLoss = 0
            status = "Open"
            description = feature.attribute("Descript") #if feature.attribute("Descript") is not None else ""
            label = "" #Esto es para escribir las etiquetas de epanet.
            node1Name = INP_Utils.get_element(node1)

            node2Name = INP_Utils.get_element(node2)

            # if self.options[INP_Options.Hydraulics].headloss == 'H-W':
            #     coef = c_H_W
            # else:
            #     coef = roughness

            coef = c_H_W if self.options[INP_Options.Hydraulics].headloss == 'H-W' else roughness

            # hydralics = self._options.classes[INP_Options.Hydraulics.name]
            # print(hydralics)
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

            pipe.values.append(Pipe(name, node1Name, node2Name, length, diameter, coef, minorLoss, status, description))

            """
            pipe_feature.setAttribute("C(H.W.)", 0)
            """

            if label != "":
                tag.values.append(Tag("LINK", id, label))

            my_id = str(feature.attribute("ID"))
            INP_Utils.add_element(my_id, [name, 'link'])


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


    def writeSections(self, path: str = None):
        self.__readLayers()
        fileName = path or self.OutFile

        # if os.path.exists(fileName):
        #     os.remove(fileName)

        with open(fileName, "w") as inpfile:
            for t, s in self.sections.items():
                # print(t, s.name)
                s.writeSection(inpfile)


    # def getResultforTime(self, time) -> Series:
    #     if self._simulation_validity:
    #         timeOpt: TimeOptions = self.options[INP_Options.Times]
    #         _, rtime, _ = INP_Utils.hora_to_int(timeOpt.duration)
            
    #         if (time <= rtime):
    #             return self._results.node[NodeResultType.pressure.name].loc[time * 3600, :]
    #     else:
    #         return None


    def removerAnalysis(self):
         # Seeliminan los layes que se crearon para motrar los resultados
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if shapeGroup:
            layer_ids = [layer.layerId() for layer in shapeGroup.findLayers()]
            root.removeChildNode(shapeGroup)
            for layer_id in layer_ids:
                QgsProject.instance().removeMapLayer(layer_id)


    def getAnalysisResults(self):
        """Se obtienen los resultados de la simulación local"""
        self.removerAnalysis()
        # Se configura el archivo del inp. aqui se debe guardar las opciones del inp si no existen.
        self.options.load()
        self.writeSections()

        wn = wntr.network.WaterNetworkModel(self.OutFile)

        inpFileTemp = os.path.dirname(self.OutFile) +"\\temp"

        # Simulate hydraulics
        sim = wntr.sim.EpanetSimulator(wn)
        # sim = wntr.sim.WNTRSimulator(wn)
        self._results = sim.run_sim(inpFileTemp)

        nodeResult_at_0hr = self._results.node[NodeResultType.pressure.name].loc[0 * 3600, :]
        linkResult_at_0hr = self._results.link[LinkResultType.flowrate.name].loc[0 * 3600, :]
        # pressure_at_5hr = results.node[NodeResultType.pressure.name].loc[0*3600, :]
        # print(pressure_at_5hr)
        self._guid = str(uuid.uuid4())
        NodeNetworkAnalysisLocal(nodeResult_at_0hr, self._guid, "00:00")
        PipeNetworkAnalysisLocal(linkResult_at_0hr, self._guid, "00:00")
        self._simulation_validity = True


    def getAnalysisResults_for_time(self, time, nodeResultType: NodeResultType = NodeResultType.pressure, linkResultType: LinkResultType = LinkResultType.flowrate):
        self.removerAnalysis()
        nodeResult_at_hour = self._results.node[nodeResultType.name].loc[time * 3600, :]
        linkResult_at_hour = self._results.link[linkResultType.name].loc[time * 3600, :]
        time_string = f"{time:02}:00"
        NodeNetworkAnalysisLocal(nodeResult_at_hour, self._guid, time_string, nodeResultType)
        PipeNetworkAnalysisLocal(linkResult_at_hour, self._guid, time_string, linkResultType)
        
        
    def getValues_for_element(self, element, typeValue, nodeResultType: NodeResultType = NodeResultType.pressure, linkResultType: LinkResultType = LinkResultType.flowrate):
        result: Series = None
        var_y = ""
        if (typeValue == 'node'):
            result = self._results.node[nodeResultType.name].loc[:, element]
            var_y = nodeResultType.name
        else:
            result = self._results.link[linkResultType.name].loc[:, element]
            var_y = linkResultType.name
        
        if (result is not None):
            x_values = [x1 / 3600 for x1 in result.index.tolist()]
            y_values = result.values

            # Crear la gráfica
            plt.plot(x_values, y_values, marker='o', linestyle='-')

            # Configurar el título y las etiquetas de los ejes
            plt.title(f"Comportamineto {element}")
            plt.xlabel("valores en hora")
            plt.ylabel(f"Valores de {var_y}")

            # Mostrar la gráfica
            plt.show()


    def getMetrics(self):
        """Se obtienen los resultados de la Resilience metrics (Hydraulic metrics)"""
        print("----------------Hydraulic metrics------------------------")

        wn = wntr.network.WaterNetworkModel(self.OutFile)

        wn.options.hydraulic.demand_model = 'PDD'

        sim = wntr.sim.WNTRSimulator(wn)
        results = sim.run_sim()

        pressure = results.node[NodeResultType.pressure.name]
        threshold = 5.4
        pressure_above_threshold = wntr.metrics.query(pressure, np.greater, threshold)
        print(f"Metric pressure above threshold ({threshold}):\n", pressure_above_threshold)

        expected_demand = wntr.metrics.expected_demand(wn)
        demand = results.node[NodeResultType.demand.name]
        wsa = wntr.metrics.water_service_availability(expected_demand, demand)
        print("Metric Water service availability:\n", wsa)

        head = results.node[NodeResultType.head.name]
        pump_flowrate = results.link[LinkResultType.flowrate.name].loc[:, wn.pump_name_list]
        todini = wntr.metrics.todini_index(head, pressure, demand, pump_flowrate, wn, threshold)
        print("Todini index:\n", todini)

        flowrate = results.link[LinkResultType.flowrate.name].loc[1*3600, :]
        G = wn.to_graph(link_weight=flowrate)
        entropy, system_entropy = wntr.metrics.entropy(G)
        print("Entropy:\n", entropy)
        print("System entropy:", system_entropy)


    def showDialog(self):

        ui = WateringINPOptionsDialog()

        ui.show()
        if ui.exec_() == 1:
            print("0001: Dialogo abierto...")
        else:
            print("0002: Dialogo cerrado...")
        # self.dlg = WateringLogin()
        # self.dlg.show()
        # if self.dlg.exec_() == 1: